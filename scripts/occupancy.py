#! /usr/bin/env python
import uproot
import pandas as pd
import numpy as np
import pickle

thresholds = [0.5, 0.75, 1., 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.75, 2., 2.25, 2.5, 2.75, 3.]
#  thresholds = [0.5, 0.75, 1., 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.75, 2., 2.25, 2.5, 2.75, 3., 3.25, 3.5, 3.75, 4., 4.25, 4.5, 4.75, 5., 5.5, 6., 7., 8., 9., 10.]
#  thresholds = [0.5, 0.75, 1., 1.25, 1.5, 2., 2.25, 2.5]
#thresholds = [1., 2.]

treename = 'hgcalTriggerNtuplizer/HGCalTriggerNtuple'
branches = ['event',
            'tc_subdet',
            'tc_zside',
            'tc_layer',
            'tc_waferurot',
            'tc_wafervrot',
            'tc_sector',
            'tc_mipPt'
           ]

tc2words = pd.read_csv('../data/ECON_TC_to_bits.csv')
tc2words.columns = ['occupancy', 'words', 'elinks']
tc2words.set_index('occupancy', inplace=True)
word0 = tc2words.loc[0]['words']
words_arr = tc2words['words'].array

def word_count(row):
    ntc = row.ntc
    return tc2words.loc[ntc]['words']

def mean_words_fromdist(row):
    return np.dot(words_arr, row.array[0])

def mean_words(group, ntotal):
    nonzeroes = group.shape[0]
    if nonzeroes==0: return word0
    zeroes = ntotal-nonzeroes
    mean = group.words.mean()
    return (mean*nonzeroes+word0*zeroes)/ntotal

def mean(group, ntotal):
    nonzeroes = group.shape[0]
    if nonzeroes==0: return 0
    zeroes = ntotal-nonzeroes
    mean = group.ntc.mean()
    return mean*nonzeroes/ntotal

def distribution(group, ntotal):
    hist = np.histogram(group['ntc'], bins=np.arange(-0.5, 49.5, step=1.))[0]
    nonzeroes = group.shape[0]
    if nonzeroes==0: return 0
    zeroes = ntotal-nonzeroes
    hist[0] = zeroes
    return hist/np.sum(hist)


def main(input_file, output_file):
    tree = uproot.open(input_file)[treename]
    df = tree.arrays(branches, library='pd')
    # Keep only silicon
    df = df.query('tc_subdet<10 & tc_mipPt>0.5')
    df = df.reset_index()
    nevents = tree.num_entries
    #nevents = df['event'].unique().shape[0]
    ntotal = nevents*6 # 3*2 sectors of 120deg
    occupancies = []
    for threshold in thresholds:
        print(threshold)
        df = df[df.tc_mipPt>threshold]
        counts = df.groupby(['entry', 'tc_zside', 'tc_layer', 'tc_sector', 'tc_waferurot', 'tc_wafervrot']).count()
        counts.rename(columns={'tc_mipPt': 'ntc'}, inplace=True)
        counts = counts.reset_index()
        means = counts.groupby(['tc_layer', 'tc_waferurot', 'tc_wafervrot']).apply(lambda x: mean(x,ntotal))
        means = means.reset_index()
        means.columns = ['layer', 'waferu', 'waferv', 'mean_occupancy']
        means.set_index(['layer', 'waferu', 'waferv'], inplace=True)
        means['occupancies'] = counts.groupby(['tc_layer', 'tc_waferurot', 'tc_wafervrot']).apply(lambda x: distribution(x, ntotal))
        means['threshold'] = threshold
        distributions = means.reset_index()[['layer', 'waferu', 'waferv', 'occupancies']].set_index(['layer', 'waferu', 'waferv']).to_dict()['occupancies']
        distributions_df = means.reset_index()[['layer', 'waferu', 'waferv', 'occupancies']].set_index(['layer', 'waferu', 'waferv'])
        means['mean_words'] = distributions_df.apply(mean_words_fromdist, axis=1)
        means = means.reset_index()[['threshold', 'layer', 'waferu', 'waferv', 'mean_occupancy', 'mean_words']]
        output_pkl = output_file.replace('.csv', '_th{}.pkl'.format(threshold))
        output_csv = output_file.replace('.csv', '_th{}.csv'.format(threshold))
        distributions_df.to_csv(output_csv)
        with open(output_pkl, 'wb') as f:
            pickle.dump(distributions, f)
        occupancies.append(means)
    pd.concat(occupancies).set_index(['threshold', 'layer', 'waferu', 'waferv']).to_csv(output_file)


if __name__=='__main__':
    import sys
    import optparse

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('--input', dest='input_file', help='Input file')
    parser.add_option('--output', dest='output_file', help='Output file', default='test.csv')
    (opt, args) = parser.parse_args()
    if not opt.input_file :
        parser.print_help()
        print('Error: Missing input file name')
        sys.exit(1)
    main(opt.input_file, opt.output_file)

