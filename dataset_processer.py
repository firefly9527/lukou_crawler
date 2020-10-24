import pandas


def generate_excel_hyperlink(link):
    return f'=HYPERLINK("{link}", "{link}")'


def filter_column(dataset):
    return pandas.DataFrame(dataset,
                            columns=['title', 'feed_url', 'text', 'collect'])


def order_by(dataset, columns, ascending):
    return dataset.sort_values(by=columns, ascending=ascending)
