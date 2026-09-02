### Title
Webhook shop identity spoofing due to HMAC covering only the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC signature over the raw body alone, while the `shop` attribute used to identify which tenant a webhook belongs to is taken from an unauthenticated header. Because Shopify webhook HMACs are computed with the app's single shared `api_secret_key` (not a per-shop secret), a payload with a valid signature can be replayed with a different `shopify-shop-domain`/`x-shopify-shop-domain` header, and `HmacValidator.validate` will still accept it, causing the host application to process attacker-controlled data attributed to a victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside of what is signed: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute and compare the HMAC solely against `verifiable_query.to_signable_string` (the raw body), never incorporating `shop`, `topic`, or any other header: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching the handler with `request.shop` as the tenant identity: [4](#0-3) 

This is the same bug class as the referenced ACO report: a field that is acted upon (`shop`, used as the tenant/session key for dispatch) is not covered by the integrity check (HMAC only binds the body). The equality that should hold is:

`shop_verified_by_hmac == shop_used_for_dispatch`

but in reality:

`shop_verified_by_hmac == "" (not present in signed content) != shop_used_for_dispatch (header value, attacker-controlled)`

Because a single app-level `api_secret_key` signs webhooks for *every* shop that installs the app, a valid `(body, hmac)` pair obtained from one tenant (e.g. the attacker's own store, or any store where the attacker can trigger/observe a webhook) remains cryptographically valid when replayed with the `shop-domain` header changed to a different, victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` object whose `shop` is the victim's domain, even though nothing about the victim shop was ever verified.

### Impact Explanation
This breaks the tenant/identity boundary the HMAC is meant to enforce: an attacker who can deliver an HTTP request to the host application's webhook endpoint (which is a public endpoint by design) can forge the apparent originating shop of a webhook while keeping a cryptographically valid signature, as long as they can produce or capture any validly-signed body for the same app. This enables cross-tenant data injection: fake `orders/create`, `app/uninstalled`, `customers/data_request`, etc. can be attributed to an arbitrary shop, potentially causing host applications to act on another merchant's data/session incorrectly (e.g., deleting/rotating a different tenant's data, or triggering GDPR-like flows for the wrong shop).

### Likelihood Explanation
Exploitability requires only network access to the app's public webhook endpoint and the ability to obtain one validly HMAC-signed payload for the app (trivial for an attacker who installs the app on their own store and captures its outbound webhooks). No credentials, access tokens, or `client_secret` are needed. This is a low-effort, unprivileged-internet-user attack path.

### Recommendation
Bind the shop identity (and other dispatch-relevant fields such as `topic`) into the value that is authenticated, not just the raw body — e.g., include the `shopify-shop-domain` and `shopify-topic` header values in the signable string used by `HmacValidator`, or require the host application to independently verify that the shop in the webhook belongs to a session/installation the app recognizes before trusting `WebhookMetadata#shop` for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and captures a legitimate webhook delivery (raw body + `x-shopify-hmac-sha256` header) — this HMAC is valid because it's signed with the app's single shared `api_secret_key`.
2. Attacker POSTs the same raw body and HMAC header to the host app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `shop` becomes `"victim.myshopify.com"`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — validation succeeds since the body/signature pair is authentic for the app.
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, causing the host application to process attacker-supplied data as though it came from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
