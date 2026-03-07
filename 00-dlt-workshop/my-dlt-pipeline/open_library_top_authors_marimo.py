from typing import List, Optional


import marimo as _mo


app = _mo.App(width="full")


@app.cell
def _():
    intro_md = _mo.md(
        """
        ## Open Library: Top 10 authors by book count

        This notebook reads the dataset produced by `open_library_pipeline` via **dlt dataset access + ibis**.
        """
    )
    # `intro_md` is the cell output


@app.cell
def _():
    import dlt

    global pipeline, dataset, dataset_name, con, tables

    pipeline = dlt.pipeline(
        pipeline_name="open_library_pipeline",
        destination="duckdb",
    )
    dataset = pipeline.dataset()
    dataset_name = dataset.dataset_name
    con = dataset.ibis()
    tables = con.list_tables(database=dataset_name)


@app.cell
def _():
    preferred = "books__authors"
    authors_table_name = preferred if preferred in tables else next(
        (t for t in tables if "authors" in t), None
    )

    if not authors_table_name:
        raise RuntimeError(
            f"Couldn't find an authors table in the dataset. "
            f"Available tables in {dataset_name!r}: {tables}"
        )

    md = _mo.md(
        f"""
        **Dataset**: `{dataset_name}`

        **Authors table**: `{authors_table_name}`
        """
    )
    # `authors_table_name` and `md` are the cell outputs


@app.cell
def _():
    authors = con.table(authors_table_name, database=dataset_name)
    cols = set(authors.columns)

    def pick(candidates: List[str]) -> Optional[str]:
        for c in candidates:
            if c in cols:
                return c
        return None

    author_name_col = pick(["name", "author_name", "full_name"])
    # `_dlt_parent_id` links each author row back to its parent book row.
    book_ref_col = pick(
        ["_dlt_parent_id", "_dlt_root_id", "book_id", "books_id", "works_id"]
    )

    if not author_name_col or not book_ref_col:
        raise RuntimeError(
            "Couldn't infer required columns from authors table. "
            f"Table columns: {sorted(cols)}"
    )

    # `authors`, `author_name_col`, `book_ref_col` are the outputs


@app.cell
def _():
    agg = authors.group_by(authors[author_name_col]).aggregate(
        book_count=authors[book_ref_col].nunique()
    )
    top10 = agg.order_by(agg.book_count.desc()).limit(10)
    top10_df = top10.execute()


@app.cell
def _():
    title_md = _mo.md("### Top 10 authors")


@app.cell
def _():
    # Try Plotly first; fall back to a table if unavailable.
    try:
        import plotly.express as px

        fig = px.bar(
            top10_df,
            x=top10_df.columns[0],
            y="book_count",
            title="Top 10 authors by book count",
        )
        fig.update_layout(xaxis_title="Author", yaxis_title="Book count")
        chart = fig
    except Exception:
        chart = _mo.ui.table(top10_df)


if __name__ == "__main__":
    app.run()
