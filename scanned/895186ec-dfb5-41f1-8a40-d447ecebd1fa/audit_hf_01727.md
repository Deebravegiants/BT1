# [M] Insecure initialization functions

## Summary
Severity: Medium
Contest weight: 0.4515
Dataset id: 9435
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the codebases, there are many initialization functions that do not have any access control. This means that an attacker can initialize them before the true caller does.
Some of these initialization functions have sensitive parameters that are set during the call such as admin keys. These include:
1. ULN::init_uln
2. pricefeed::init_price_feed
3. oft::init_oft
4. oft::init_adapter_oft
5. executor::init_executor
6. endpoint::init_endpoint
7. dvn::init_dvn
Here is an example of the ULN initialization that has no access control:
```solidity
#[instruction(params: InitUlnParams)]
pub struct InitUln<'info> {
    #[account(mut)]
    pub payer: Signer<'info>,
    #[account(
        init,
        payer = payer,
        space = 8 + UlnSettings::INIT_SPACE,
        seeds = [ULN_SEED],
    )]
    pub uln: Account<'info, UlnSettings>,
    pub system_program: Program<'info, System>,
}

impl InitUln<'_> {
    pub fn apply(ctx: &mut Context<InitUln>, params: &InitUlnParams) -> Result<()> {
        ctx.accounts.uln.eid = params.eid;
        ctx.accounts.uln.endpoint = params.endpoint;
        ctx.accounts.uln.endpoint_program = params.endpoint_program;
        ctx.accounts.uln.admin = params.admin;
        ctx.accounts.uln.treasury = None;
        ctx.accounts.uln.treasury_fee_cap = params.treasury_fee_cap;
        ctx.accounts.uln.treasury_admin = params.treasury_admin;
        ctx.accounts.uln.bump = ctx.bumps.uln;
        Ok(())
    }
}
```
Since these init functions cannot be called directly at program deployment - an attacker can call them before the deployer and set arbitrary parameters (including admin keys). This might not be noticed by the deployer and the hacker could gain privileges to the program or it will be noticed and the program will be redeployed (maybe multiple times).

## Recommendation
The deployer or other known address should be verified in the init function.
Anchor docs suggest using the upgrade_authority_address: link
