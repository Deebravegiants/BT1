# [?] lp: fix: migrate 0 panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-11-24
Source: https://github.com/filecoin-project/lotus/commit/37d5d59eccd0ce38373a602139ca187b6864a407
Type: security-commit

## Details
lp: fix: migrate 0 panic

## Patch
### chain/types/fil.go
```diff
@@ -12,6 +12,9 @@ import (
 type FIL BigInt
 
 func (f FIL) String() string {
+	if f.Int == nil {
+		return "0 FIL"
+	}
 	return f.Unitless() + " FIL"
 }
 
```

### cmd/lotus-provider/migrate.go
```diff
@@ -11,6 +11,7 @@ import (
 	"strings"
 
 	"github.com/BurntSushi/toml"
+	"github.com/fatih/color"
 	"github.com/ipfs/go-datastore"
 	"github.com/samber/lo"
 	"github.com/urfave/cli/v2"
@@ -27,6 +28,7 @@ import (
 
 var configMigrateCmd = &cli.Command{
 	Name:        "from-miner",
+	Usage:       "Express a database config (for lotus-provider) from an existing miner.",
 	Description: "Express a database config (for lotus-provider) from an existing miner.",
 	Flags: []cli.Flag{
 		&cli.StringFlag{
@@ -48,8 +50,8 @@ var configMigrateCmd = &cli.Command{
 			Usage:   "The layer name for this data push. 'base' is recommended for single-miner setup.",
 		},
 		&cli.BoolFlag{
-			Name:    "replace",
-			Aliases: []string{"r"},
+			Name:    "overwrite",
+			Aliases: []string{"o"},
 			Usage:   "Use this with --to-layer to replace an existing layer",
 		},
 	},
@@ -64,6 +66,8 @@ const FlagMinerRepoDeprecation = "storagerepo"
 
 func fromMiner(cctx *cli.Context) (err error) {
 	ctx := context.Background()
+	cliCommandColor := color.New(color.FgHiBlue).SprintFunc()
+	configColor := color.New(color.FgHiGreen).SprintFunc()
 
 	r, err := repo.NewFS(cctx.String(FlagMinerRepo))
 	if err != nil {
@@ -111,7 +115,7 @@ func fromMiner(cctx *cli.Context) (err error) {
 			return errors.New("the overwrite flag is needed to replace existing layer: " + name)
 		}
 	}
-	msg := "Layer " + name + ` created. `
+	msg := "Layer " + configColor(name) + ` created. `
 
 	// Copy over identical settings:
 
@@ -163,16 +167,16 @@ func fromMiner(cctx *cli.Context) (err error) {
 
 	ainfo, err := cliutil.GetAPIInfo(&cli.Context{}, repo.FullNode)
 	if err != nil {
-		return xerrors.Errorf("could not get API info for FullNode: %w", err)
+		return xerrors.Errorf(`could not get API info for FullNode: %w
+		Set the environment variable to the value of "lotus auth api-info --perm=admin"`, err)
 	}
 	lpCfg.Apis.ChainApiInfo = []string{header.Get("Authorization")[7:] + ":" + ainfo.Addr}
 
 	// Enable WindowPoSt
 	lpCfg.Subsystems.EnableWindowPost = true
-	msg += `\nBefore running lotus-provider, ensure any miner/worker answering of WindowPost is disabled by
-(on Miner) DisableBuiltinWindowPoSt=true and (on Workers) not enabling windowpost on CLI or via
-environment variable LOTUS_WORKER_WINDOWPOST.
-`
+	msg += "\nBefore running lotus-provider, ensure any miner/worker answering of WindowPost is disabled by " +
+		"(on Miner) " + configColor("DisableBuiltinWindowPoSt=true") + " and (on Workers) not enabling windowpost on CLI or via " +
+		"environment variable " + configColor("LOTUS_WORKER_WINDOWPOST") + "."
 
 	// Express as configTOML
 	configTOML := &bytes.Buffer{}
@@ -217,11 +221,10 @@ environment variable LOTUS_WORKER_WINDOWPOST.
 
 	msg += `
 To work with the config:
-./lotus-provider ` + dbSettings + ` config help `
+` + cliCommandColor(`lotus-provider `+dbSettings+` config help `)
 	msg += `
 To run Lotus Provider: in its own machine or cgroup without other files, use the command: 
-./lotus-provider ` + dbSettings + ` run --layers="` + name + `"
-	`
+` + cliCommandColor(`lotus-provider `+dbSettings+` run --layers="`+name+`"`)
 	fmt.Println(msg)
 	return nil
 }
```
