#!/usr/bin/env python
# [SublimeLinter pep8-max-line-length:300]
# -*- coding: utf-8 -*-

"""
ruby_rhino is a multi-agent simulator for financial network analysis
Copyright (C) 2016 Paweł Fiedor (pawel@fiedor.eu)

Based on black_rhino available on Github

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""

import logging
import random

"""
  class Shock
"""


class Shock(object):
    #
    # VARIABLES
    #

    #
    # METHODS
    #
    def do_shock(self, environment, time):
        largest_exposure = 0.0
        largest_bank = environment.banks[0]

        shock_type = int(environment.get_state(time).shockType)
        logging.info("      shock of type %s executed at time %s", shock_type, time)
        if shock_type == 1:
            # select the largest banks in terms of interbank exposures
            largest_bank = self.find_largest_bank(environment)
            # now send the largest bank into default
            largest_bank.reduce_banking_capital(10.0)
            largest_bank.check_solvency("info",  time)

        if shock_type == 2:
            # select the largest banks in terms of interbank exposures
            largest_bank = self.find_largest_bank(environment)
            # now send the largest bank into default
            largest_bank.parameters["Lp"] = -10.0
    # -------------------------------------------------------------------------

    def do_shock_asset(self, environment, time):

        shock_type = int(environment.get_state(time).shockType)
        logging.info("      shock of type %s executed at time %s", shock_type, time)
        if shock_type == 3:
            # random asset gets devalued
            # go through all investments and reduce value of the asset
            shocked_asset = ""
            shocked_asset = random.choice(environment.list_of_assets)  # we chose randomly from a list of assets

            # now reduce the value of all investment of the chosen type
            for bank in environment.banks:
                bank_pre_sell = 0.0
                for tranx in bank.accounts:
                    if tranx.transactionAsset == shocked_asset:
                        bank_pre_sell += tranx.transactionValue
                        tranx.transactionValue = (1 - environment.static_parameters["AssetShockLoss"]) * tranx.transactionValue
                bank.parameters["shockAssetsPreLoss"] = bank_pre_sell
            self.do_fire_sales(environment, shocked_asset, min_dummie)

        if shock_type == 4:
            # biggest asset gets devalued
            # go through all investments and reduce value of the asset
            shocked_asset = ""  # below we find the asset with maximum holdings overall
            max_dummie = -1  # all transaction values are positive so this will always be fine
            for test_asset in environment.list_of_assets:
                sum_dummie = 0  # sum total value of the given asset across all banks and holdings
                for bank in environment.banks:
                    for tranx in bank.accounts:
                        if tranx.transactionAsset == test_asset:
                            sum_dummie = sum_dummie + tranx.transactionValue
                if sum_dummie > max_dummie:  # if the sum of the asset is bigger than the current max change the max value / asset type
                    max_dummie = sum_dummie
                    shocked_asset = test_asset

            # now reduce the value of all investment of the chosen type
            for bank in environment.banks:
                bank_pre_sell = 0.0
                for tranx in bank.accounts:
                    if tranx.transactionAsset == shocked_asset:
                        bank_pre_sell += tranx.transactionValue
                        tranx.transactionValue = (1 - environment.static_parameters["AssetShockLoss"]) * tranx.transactionValue
                bank.parameters["shockAssetsPreLoss"] = bank_pre_sell
            self.do_fire_sales(environment, shocked_asset, min_dummie)

        if shock_type == 5:
            # smallest asset gets devalued
            # go through all investments and reduce value of the asset
            shocked_asset = ""
            min_dummie = -1  # separate starting condition below for -1
            for test_asset in environment.list_of_assets:
                sum_dummie = 0  # sum total value of the given asset across all banks and holdings
                for bank in environment.banks:
                    for tranx in bank.accounts:
                        if tranx.transactionAsset == test_asset:
                            sum_dummie = sum_dummie + tranx.transactionValue
                if min_dummie == -1:  # starting condition, if this is the first checked asset we set it to be the minimum for now
                    min_dummie = sum_dummie
                    shocked_asset = test_asset
                else:
                    if sum_dummie < min_dummie:  # if the sum of the asset is bigger than the current min change the min value / asset type
                        min_dummie = sum_dummie
                        shocked_asset = test_asset

            # now reduce the value of all investment of the chosen type
            for bank in environment.banks:
                bank_pre_sell = 0.0
                for tranx in bank.accounts:
                    if tranx.transactionAsset == shocked_asset:
                        bank_pre_sell += tranx.transactionValue
                        tranx.transactionValue = (1 - environment.static_parameters["AssetShockLoss"]) * tranx.transactionValue
                bank.parameters["shockAssetsPreLoss"] = bank_pre_sell
            self.do_fire_sales(environment, shocked_asset)
    # -------------------------------------------------------------------------

    def do_fire_sales(self, environment, shocked_asset, preValue):
        for asset in environment.list_of_assets:
            environment.list_of_firesold[asset] = 0

        for bank in environment.banks:
            leverage = bank.find_leverage()
            to_sell = (1 - environment.static_parameters["AssetShockLoss"]) * bank.parameters["shockAssetsPreLoss"] * leverage
            all_investments = self.get_account("I")
            fire_sold = 0.0
            for tranx in bank.accounts:
                if tranx.transactionType == "I":
                    fire_sold += (tranx.transactionValue / all_investments) * to_sell
                    environment.list_of_firesold[tranx.transactionAsset] += (tranx.transactionValue / all_investments) * to_sell
                    tranx.transactionValue = tranx.transactionValue - (tranx.transactionValue / all_investments) * to_sell
            bank.parameters["shockAssetsFireSold"] = fire_sold
        # what about capital?
        # price depreciation with the proportions to the wealth of the system
        liquidity = 10**-13  # 10 basis points price change per $10 billion of trading imbalances, from Duarte/Eisenbach >> corporate bonds in August 2011
        # for the above we need real data, for simulation we need to use appropriate scale or change this so it makes sense
        for bank in environment.banks:
            for tranx in bank.accounts:
                if tranx.transactionType == "I":
                    tranx.transactionValue = tranx.transactionValue - liquidity * environment.list_of_firesold[tranx.transactionAsset]
        # remove loans for the sold amount
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # find_largest_bank()
    # this routine finds the largest bank in terms of interbank exposure
    # -------------------------------------------------------------------------
    def find_largest_bank(self,  environment):
        largest_exposure = 0.0
        largest_bank = environment.banks[0]
        for bank in environment.network.exposures.nodes():
            exposure = 0.0
            for neighbor in environment.network.exposures[bank]:
                exposure += environment.network.exposures[bank][neighbor]['weight']
            if (exposure > largest_exposure):  # we have a new largest bank
                largest_exposure = exposure
                largest_bank = bank
        return largest_bank
    # -------------------------------------------------------------------------
