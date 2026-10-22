# [M] Missed Arbitrage Profits from Imbalanced Pools

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-06
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/101
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/d47eae920d5840afadd5fd5d1fd0d6da0107c034/src/arbitrage/ArbitrageSearch.sol#L132


# Vulnerability details

# Lines of code

https://github.com/othernet-global/salty-io/blob/d47eae920d5840afadd5fd5d1fd0d6da0107c034/src/arbitrage/ArbitrageSearch.sol#L115-L133

# C4 issue

M-16: Suboptimal arbitrage implementation


# Comments

The issue addressed the protocol's potential to overlook profitable trades due to its search range limitations. The bisection search method employed by the protocol might miss profit opportunities when the pools are balanced and a user wants to swap an amount of one token for another. This is crucial since arbitrage is a key feature that should always be available to users for capitalizing on price differences across various liquidity pools.

# Mitigation

https://github.com/othernet-global/salty-io/commit/a54656dd18135ca57eef7c4bf615b7cdff2613a7

The mitigation succesfully implemented the updated ArbitrageSearch algorithm to follow suit with the math and also the example code provided in the issue, but it additionally made sure the overflow risk is reduced since the math involves multiplications of multiple reserves(which could be substantial) primarily in the calculations of n1 and n0.

However upon further inspection, an edge case arises where if the pools were severely imbalanced, this scenario can occur:

1. One of the reserves has a MSB more than 80.
2. All reserves are shifted by "shift = maximumMSB - 80" to ensure none of them is more than 80 bits.
3. However some reserves are too low, and shifting them by this magnitude sets them to equal 0.
4. those reserves shifted to zero set n1 and n0 to 0.
5. the check that n1 <= n0 is true and function returns 0, even though n1 could have been higher than n0 before the shift.


# Impact

As with the original intention of the issue, there is potential for the algorithm to miss arbitrage profits, albeit due to a different reason and under a different circumstance, which applies here when the pools are imbalanced, and to how overflow is handled in the calculations.

# Proof of Concept

    	function testArbitrageMethods() public view {
            // Initial, roughly balanced pools
            // 18 ETH ~ 1 BTC ~ 40k TOKEN A
            // uint256 reservesA0 = 900 ether; // ETH
            // uint256 reservesA1 = 2000000 ether; // TOKEN A
            // uint256 reservesB0 = 4000000 ether; // TOKEN A
            // uint256 reservesB1 = 100 ether; // BTC
            // uint256 reservesC0 = 500 ether; // BTC
            // uint256 reservesC1 = 9000 ether; // ETH

			uint256 reservesA0 = 90000000; // ETH
			uint256 reservesA1 = 900000000; // TOKEN A
			uint256 reservesB0 = 900000000; // TOKEN A
			uint256 reservesB1 = 200000000100 ether; // TOKEN B
			uint256 reservesC0 = 1500000000; // TOKEN B
			uint256 reservesC1 = 1000 ether; // ETH

            for (uint256 i = 0; i < 4; i++) {

                console.log("");

                uint256 bestApproxProfit;
                uint256 auxReservesB1;
                uint256 auxReservesB0;

                {
                    // Swap BTC for TOKEN A
                    uint256 swapAmountInValueInBTC = 1 ether * (i + 1);  // Arbitrary value for test
                    console.log(i, "- swap", swapAmountInValueInBTC / 10 ** 18, "BTC for TOKEN A");
                    auxReservesB1 = reservesB1 + swapAmountInValueInBTC;
                    auxReservesB0 = reservesB0 - reservesB0 * swapAmountInValueInBTC / auxReservesB1;

					uint256 gas0 = gasleft();
                    uint256 bestBrute = _bruteForceFindBestArbAmountIn(swapAmountInValueInBTC / 18, reservesA0, reservesA1, auxReservesB0, auxReservesB1, reservesC0, reservesC1);
					console.log( "BRUTE GAS: ", gas0 - gasleft() );

                    console.log("Original brute arbitrage estimation: ", bestBrute);
                    bestApproxProfit = getArbitrageProfit(bestBrute, reservesA0, reservesA1, auxReservesB0, auxReservesB1, reservesC0, reservesC1);
                    console.log("Brute arbitrage profit: ", bestApproxProfit);
                }

				uint256 bestExact;
				unchecked
					{
					uint256 gas0 = gasleft();
                	bestExact = _bestArbitrageIn(reservesA0, reservesA1, auxReservesB0, auxReservesB1, reservesC0, reservesC1);
					console.log( "BEST GAS: ", gas0 - gasleft() );
					}

                console.log("Best arbitrage computation: ", bestExact);
                uint256 bestExactProfit = getArbitrageProfit(bestExact, reservesA0, reservesA1, auxReservesB0, auxReservesB1, reservesC0, reservesC1);
                console.log("Best arbitrage profit: ", bestExactProfit);

				// Assumes an ETH price of $2300
				if (bestExactProfit > bestApproxProfit)
                console.log("PROFIT IMPROVEMENT (in USD cents): ", 2300 * (bestExactProfit - bestApproxProfit) / 10 ** 16);
				if (bestApproxProfit > bestExactProfit)
				console.log("PROFIT DECREASE (in USD cents): ", 2300 * (bestApproxProfit - bestExactProfit) / 10 ** 16);
            }
        }


THe POC above has reserve values which simulate the imbalanced pools scenario. It also shows the missed arbitrage profits through using the new algorithm compared with the brute force method.


# Recommendation

Explore ways to handle overflow that will not impact potential arbitrage profits.














## Assessed type

Math
