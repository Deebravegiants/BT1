## Title
Webhook `Registry.process` trusts the `shop` (and `topic`/`api_version`/`webhook_id`) header value even though `HmacValidator` only signs the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the `X-Shopify-Hmac-Sha256` signature, then hands the handler a `shop` value taken from an HTTP header that is never part of the signed material. This breaks the identity binding "the shop that was cryptographically authenticated == the shop the handler is told the data belongs to."

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers instead: [2](#0-1) 

`Registry.process` verifies the HMAC and, if it matches, immediately trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` passed to the app's handler — with no additional binding between the authenticated body and the shop identity: [3](#0-2) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`: [4](#0-3) 

Because webhooks for all shops installed on a given app are signed with the same `api_secret_key`, an unprivileged internet user can:
1. Install the target app on their own (attacker-controlled) development/trial shop — no privileged access needed.
2. Receive a legitimately signed webhook (e.g. `app/uninstalled`, `customers/redact`, `orders/create`) whose raw body produces a *valid* HMAC.
3. Replay that exact `raw_body` + `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain.

`HmacValidator.validate` still returns `true` (the body/HMAC pair is unchanged and valid), and `Registry.process` will invoke the handler with `WebhookMetadata#shop == victim_shop` while `body` is attacker-controlled data from the attacker's own shop. This is exactly the identity-binding break called out in the report class: *"a field acted on but not covered by the HMAC."*

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (returned as authenticated) to select which tenant's record to update/delete — e.g. treating a forged `app/uninstalled` or `shop/redact` webhook as authoritative for the victim shop, or writing attacker-supplied order/customer data into the victim's tenant scope — suffers cross-tenant data corruption/injection. Since mandatory compliance webhooks (`customers/redact`, `shop/redact`) are commonly wired to destructive operations (deleting merchant/customer data), this can result in an attacker triggering data loss or false uninstall/de-provisioning for a shop they don't control — a cross-tenant impact.

### Likelihood Explanation
Exploitation requires only: (a) free/self-serve installation of the target app on an attacker-owned store to obtain one legitimately signed webhook, and (b) sending a forged HTTP request with a modified header to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — matching the "unprivileged internet user" threat model in scope.

### Recommendation
Bind the shop identity to the authenticated material instead of trusting the unsigned header:
- Cross-check `request.shop` against the shop that is actually authorized/enrolled for the specific `webhook_id`/topic combination before invoking the handler, or
- Require the host application to verify that the `shop` in `WebhookMetadata` corresponds to a shop with an active, expected registration for this exact webhook, or
- Where feasible, include `shop`, `topic`, and `webhook_id` in the signable string used for verification so the signature binds the full identity, not just the body.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker-shop.myshopify.com"
# and captures a legitimate webhook delivery, e.g.:
raw_body = '{"id":123, ...}'                      # from attacker's own shop
valid_hmac = "<value Shopify computed for raw_body using the app's shared api_secret_key>"

# Attacker forges a replayed request to the app's public webhook endpoint,
# keeping raw_body/hmac identical (still valid) but swapping the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # unsigned, attacker-controlled
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/HMAC pair unchanged)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...))
# The handler now believes attacker-controlled data is authenticated as belonging to victim-shop.
``` [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
