__author__ = 'ratcave'

def read_and_pop_pickle_list(filename):
    import pickle
    """Permanently pops an item from a list stored in a single-object pickle file."""

    # Get item
    with open(filename) as listfile:
        ll = pickle.load(listfile)
    item = ll.pop()

    # Write new list
    with open(filename, 'w') as listfile:
        pickle.dump(ll, listfile)

    return item