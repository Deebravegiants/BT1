# [M] If old coefficient is bigger than

## Summary
Severity: Medium
Contest weight: 0.2460
Dataset id: 23074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the old coefficient are bigger than the new coefficient, then our reputer's coefficients will be set to smaller value which will be lower than the minimum limit, essentially breaking the minStakeFraction invariant.
Vulnerability
The root cause of this issue is located in GetAllReputersOutput, in the place where if listenedStakeFraction<minStakeFraction we calculate a custom coeff.
s/module/rewards/rewards_internal.go
if listenedStakeFraction.Lt(minStakeFraction) {
for l := range coefficients {
coeffDiff, err := coefficients[l].Sub(oldCoefficients[l])
if err != nil {
return nil, nil, err
}
listenedDiff, err := minStakeFraction.Sub(listenedStakeFractionOld)
if err != nil {
return nil, nil, err
}
stakedFracDiff, err := listenedStakeFraction.Sub(listenedStakeFractionOld)
if err != nil {
return nil, nil, err
}
If our listenedStakeFractionOld is bigger than our listenedStakeFraction then stakedFracDiff will be negative. This value is later used to calculate our new coefficients bellow, where we first calculate the diff - coeffDiffTimesListenedDiff, then divide it by our fraction diff (where the actual issue is) and finally add it to oldCoefficients to get the new coefficients.
s/module/rewards/rewards_internal.go#L560
if stakedFracDiff.IsZero() {
i = gradientDescentMaxIters
} else {
coeffDiffTimesListenedDiff, err := coeffDiff.Mul(listenedDiff)
if err != nil {
return nil, nil, err
}
coefDiffTimesListenedDiffOverStakedFracDiff, err :=
coeffDiffTimesListenedDiff.Quo(stakedFracDiff)
if err != nil {
return nil, nil, err
}
coefficients[l], err =
oldCoefficients[l].Add(coefDiffTimesListenedDiffOverStakedFracDiff)
if err != nil {
return nil, nil, err
}
}
In short, if listenedStakeFraction is bellow the min allowed fraction - minStakeFraction (MinStakeFraction in the params) then we do some custom math to increase a our reputer coefficient. However as stated above that is not the case when our listenedStakeFraction is less than listenedStakeFractionOld.
Path
We got over why it happens, now lets cover the context around it - aka. how it can happen.
GetAllReputersOutput (where the issue is), is called inside GenerateReputerScores in order to calculate our scores and coefficients. Both old and new fractions are calculated with the bellow formulas:
listenedStakeFractionOld=sum(oldCoefficients*stakes)/sum(stakes) code is here listenedStakeFraction=sum(newCoefficients*stakes)/sum(stakes) code is here
In order to understand these fractions better we need to look into how they are calculated. listenedStakeFractionOld is just the last fraction from the prev. epoch, so I will skip it's math (because it's the same).
Our newCoefficients is calculated from this code snippet, implementing this formula:
min(
max(
coefficient + (learningRate * gradient)
, 0)
, 1)
Where:
1. coefficient is our old coeff.
2. learningRate is static variable (0.05)
3. gradient is the variable that can most dramatically change our newCoefficients.
gradient is calculated with the bellow formula: gradient[i]=(1-sum(score*stake)/sum(score2*stake))/(0.001||-0.001) code is here
Where our dcoeff, aka the last part - /(0.001||-0.001) will divide our numerator - (1-sum(score*stake)/sum(score2*stake)) by 0.001 or -0.001, based on if our prev. coeff was 1.
Division by numbers smaller than 1 is same as multiplication, so this can be interpreted as *(1000||-1000).
s/module/rewards/rewards_internal.go#L462-L465
dcoeff := alloraMath.MustNewDecFromString("0.001")
if coefficients[l].Equal(alloraMath.OneDec()) {
dcoeff = alloraMath.MustNewDecFromString("-0.001")
}
With all of that math behind us we can conclude that in order for listenedStakeFraction to be less than listenedStakeFractionOld our gradient needs to change. The bad news is that our gradient changes on every epoch with every score calculation, as if our prev. coeff was 1, our gradient will flip to negative, impacting slightly listenedStakeFraction, potentially making it smaller than listenedStakeFractionOld.
The effects of all of that are:
1. Breaking of invariant like minStakeFraction, as it should increase the fraction slighly when we are bellow minStakeFraction, but instead it reduces it even more.
2. Reducing reputers rewards, by reducing their coefficient more than it should. Rewards are calculated based on scores and scores are calculates with these coefficients.
stakedFracDiff, err := listenedStakeFraction.Sub(listenedStakeFractionOld)
...
} else {
coeffDiffTimesListenedDiff, err := coeffDiff.Mul(listenedDiff)
if err != nil {
return nil, nil, err
}
coefDiffTimesListenedDiffOverStakedFracDiff, err :=
coeffDiffTimesListenedDiff.Quo(stakedFracDiff)
if err != nil {
return nil, nil, err
}
coefficients[l], err =
oldCoefficients[l].Add(coefDiffTimesListenedDiffOverStakedFracDiff)
if err != nil {
return nil, nil, err
}
}

## Recommendation
A good solution would be to .abs() the value in order to make sure it is always positive.
