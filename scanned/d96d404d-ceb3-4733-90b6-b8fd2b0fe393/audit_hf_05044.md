# [H] Malicious Reputer cause emis-

## Summary
Severity: High
Contest weight: 0.3740
Dataset id: 23048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious Reputer passing in abnormal data causes InsertBulkReputerPayload to fail.
The synth.CalcNetworkLosses function computes all data in bundles, InsertBulkReputerPayload -> synth.CalcNetworkLosses -> RunningWeightedAvgUpdate
func RunningWeightedAvgUpdate(
runningWeightedAvg *RunningWeightedLoss,
nextWeight Weight,
nextValue Weight,
) (RunningWeightedLoss, error) {
nextValTimesWeight, err := nextValue.Mul(nextWeight)
if err != nil {
return RunningWeightedLoss{}, err
}
newUnnormalizedWeightedLoss, err := runningWeightedAvg.UnnormalizedWeightedLoss.Add(nextValTimesWeight)
if err != nil {
return RunningWeightedLoss{}, err
}
newSumWeight, err := runningWeightedAvg.SumWeight.Add(nextWeight)
if err != nil {
return RunningWeightedLoss{}, err
}
return RunningWeightedLoss{
UnnormalizedWeightedLoss: newUnnormalizedWeightedLoss,
SumWeight: newSumWeight,
}, nil
}
nextValue * nextWeight If the value exceeds the maximum value of unit128, a failure is returned. As a result, InsertBulkReputerPayload fails.
networkLossBundle, err := synth.CalcNetworkLosses(stakesByReputer, bundles, params.Epsilon)
if err != nil {
return nil, err
}
Malicious reputers can pass in a larger CombinedValue(nextValue) and it will return an error, bundles array stores data from a number of Reputer. Execution will fail if one of the Reputer is malicious.
The following test code demonstrates CalcNetworkLosses execution failure:
func getTestCasesTwoWorkers() []struct {
name string
stakesByReputer map[inference_synthesis.Worker]cosmosMath.Int
reportedLosses emissions.ReputerValueBundles
epsilon alloraMath.Dec
expectedOutput emissions.ValueBundle
expectedError error
} {
return []struct {
name string
stakesByReputer map[inference_synthesis.Worker]cosmosMath.Int
reportedLosses emissions.ReputerValueBundles
epsilon alloraMath.Dec
expectedOutput emissions.ValueBundle
expectedError error
}{
{
name: "simple two reputer combined loss",
stakesByReputer: map[inference_synthesis.Worker]cosmosMath.Int{
"worker1": inference_synthesis.CosmosIntOneE18(), // 1 token
"worker2": inference_synthesis.CosmosIntOneE18().MulRaw(2), // 2 tokens
},
reportedLosses: emissions.ReputerValueBundles{
ReputerValueBundles: []*emissions.ReputerValueBundle{
{
ValueBundle: &emissions.ValueBundle{
Reputer: "worker1",
CombinedValue: alloraMath.MustNewDecFromString("1e99999"), abnormal data
NaiveValue: alloraMath.MustNewDecFromString("0.1"),
InfererValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.1"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.1"),
},
},
ForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.1"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.1"),
},
},
OneOutInfererValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.1"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.1"),
},
},
OneOutForecasterValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.1"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.1"),
},
},
OneInForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.1"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.1"),
},
},
},
},
{
ValueBundle: &emissions.ValueBundle{
Reputer: "worker2",
CombinedValue: alloraMath.MustNewDecFromString("0.2"),
NaiveValue: alloraMath.MustNewDecFromString("0.2"),
InfererValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.2"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.2"),
},
},
ForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.2"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.2"),
},
},
OneOutInfererValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.2"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.2"),
},
},
OneOutForecasterValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.2"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.2"),
},
},
OneInForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.2"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.2"),
},
},
},
},
},
},
epsilon: alloraMath.MustNewDecFromString("1e-4"),
expectedOutput: emissions.ValueBundle{
CombinedValue: alloraMath.MustNewDecFromString("0.166666666"),
NaiveValue: alloraMath.MustNewDecFromString("0.166666666"),
InfererValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
},
ForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
},
OneOutInfererValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
},
OneOutForecasterValues: []*emissions.WithheldWorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
},
OneInForecasterValues: []*emissions.WorkerAttributedValue{
{
Worker: "worker1",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
{
Worker: "worker2",
Value: alloraMath.MustNewDecFromString("0.166666666"),
},
},
},
expectedError: nil,
},
}
}
func (s *InferenceSynthesisTestSuite) TestCalcNetworkLosses2() {
tests := getTestCasesTwoWorkers()
//require := s.Require()
for _, tc := range tests {
s.Run(tc.name, func() {
output , err := inference_synthesis.CalcNetworkLosses(tc.stakesByReputer, tc.reportedLosses, tc.epsilon)
fmt.Println(err)
fmt.Println(output)
})
}
}
Put the test code into the test file: allora-chain/x/emissions/keeper/inference_synthesis/network_losses_test.go
cd allora-chain/x/emissions/keeper/inference_synthesis/ go test -v -run TestModuleTestSuite/TestCalcNetworkLosses2
Error updating running weighted average for next combined loss: decimal multiplication error: exponent out of range [/home/zhaojie/hacks/2024-06-allora-zhaojio/allora-chain/math/dec.go:269]
{0 <nil> [] 0 [] [] 0 [] [] []} -
InsertBulkReputerPayload fails to be executed. As a result, data of the Reputers cannot be submitted

## Recommendation
Perform security checks on data submitted by Reputers.
