# [?] fix(vald): panic on start up (#338)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-03-11
Source: https://github.com/axelarnetwork/axelar-core/commit/521d8ac30cb81c4b1bb9bf9b3e8d8400edc16f22
Type: security-commit

## Details
fix(vald): panic on start up (#338)

Fixed panic triggered by viper package and also a flag that should be declared as persistent

## Patch
### cmd/vald/main.go
```diff
@@ -25,18 +25,11 @@ func main() {
 		Short: "Validator Daemon ",
 	}
 
-	setPersistentFlags(rootCmd)
-
-	axConf, valAddr := loadConfig()
-	if valAddr == "" {
-		tmos.Exit("validator address not set")
-	}
-
-	l := log.NewTMLogger(os.Stdout).With("external", "main")
-
-	startCommand := getStartCommand(axConf, valAddr, l)
+	startCommand := getStartCommand(log.NewTMLogger(os.Stdout).With("external", "main"))
 	rootCmd.AddCommand(flags.PostCommands(startCommand)...)
 
+	setPersistentFlags(rootCmd)
+
 	executor := cli.PrepareMainCmd(rootCmd, "AX", app.DefaultNodeHome)
 	err := executor.Execute()
 	if err != nil {
@@ -54,7 +47,7 @@ func configurate() {
 
 func setPersistentFlags(rootCmd *cobra.Command) {
 	rootCmd.PersistentFlags().String(cliHomeFlag, app.DefaultCLIHome, "directory for cli config and data")
-	_ = viper.BindPFlag(cliHomeFlag, rootCmd.Flags().Lookup(cliHomeFlag))
+	_ = viper.BindPFlag(cliHomeFlag, rootCmd.PersistentFlags().Lookup(cliHomeFlag))
 
 	rootCmd.PersistentFlags().String("tofnd-host", "", "host name for tss daemon")
 	_ = viper.BindPFlag("tofnd_host", rootCmd.PersistentFlags().Lookup("tofnd-host"))
```

### cmd/vald/start.go
```diff
@@ -27,7 +27,7 @@ import (
 	tss "github.com/axelarnetwork/axelar-core/x/tss/types"
 )
 
-func getStartCommand(axConf app.Config, valAddr string, logger log.Logger) *cobra.Command {
+func getStartCommand(logger log.Logger) *cobra.Command {
 	return &cobra.Command{
 		Use: "start",
 		RunE: func(cmd *cobra.Command, args []string) error {
@@ -36,6 +36,11 @@ func getStartCommand(axConf app.Config, valAddr string, logger log.Logger) *cobr
 				return err
 			}
 
+			axConf, valAddr := loadConfig()
+			if valAddr == "" {
+				tmos.Exit("validator address not set")
+			}
+
 			logger.Info("Start listening to events")
 			err = listen(hub, axConf, valAddr, logger)
 			if err != nil {
```
