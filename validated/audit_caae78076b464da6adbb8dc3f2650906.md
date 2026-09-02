### Title
Webhook `shop` identity not bound to HMAC signature enables cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, while `HmacValidator` only signs the raw request body. The HMAC therefore proves that *some* holder of the app's shared `client_secret` produced the body, but it never binds that body to the specific shop the request claims to be from. This mirrors the reported bug class: a related identity-carrying field (here, `shop`) is acted upon (used as the tenant key passed to the webhook handler) without being covered by the same integrity check that authenticates the payload — exactly like `validatorBondShare`/`LiquidShares` not being reduced alongside the `Unbond` call in the original report.

### Finding Description
- `Utils::HmacValidator.validate` computes/verifies the signature strictly over `verifiable_query.to_signable_string`. [1](#0-0) 
- For webhooks, `to_signable_string` returns only `@raw_body` — the topic, api-version, webhook-id, and crucially the `shop-domain` header are excluded from what is HMAC-verified. [2](#0-1) 
- `Registry.process` validates the HMAC and then immediately trusts `request.shop` (sourced straight from the unauthenticated header) as the tenant identity forwarded to the app's handler, with no cross-check that this shop is consistent with anything cryptographically bound to the body. [3](#0-2) 

Because the `client_secret` used to compute the HMAC is a single, shared per-app secret (not per-shop), any merchant who installs the same app on their own store can legitimately obtain a validly HMAC-signed `(body, hmac)` pair for arbitrary body content of their choosing (e.g., by triggering `orders/create` on their own store, or by using their own app credentials in local testing since the same secret is shared across all installs). Since the `shop-domain` header is not part of the signed material, that same valid `(body, hmac)` pair remains valid when sent directly to the app's public webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The equality the code implicitly (and incorrectly) assumes is:

`HMAC-verified(raw_body) == HMAC-verified(raw_body, shop)`

but in reality only the left side is true — `shop` is parsed, not verified.

### Impact Explanation
This breaks the tenant/authentication boundary of the webhook pipeline: an attacker who controls a legitimate (even free/trial) shop running the same app can inject attacker-controlled webhook payloads that the app's handler will process *as if they originated from a different, victim shop* — a direct cross-tenant access primitive against any Devin/host application relying solely on this gem's HMAC + `shop` extraction to authenticate webhook events per tenant (e.g. updating order/customer/inventory records keyed by `shop`).

### Likelihood Explanation
Any external actor able to install the target app on a store they control (a normal, low-privilege action for public/unlisted Shopify apps) can generate valid `(body, hmac)` pairs at will and replay them with a forged `shop-domain` header directly to the app's public webhook URL, which must be internet-reachable by design. No access token, `api_secret_key`, or victim credentials are required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable payload (or otherwise cryptographically bind the shop header to the signed body before trusting it), and/or require the caller to supply the expected shop and compare it against a value that is itself authenticated, rather than passing the raw unauthenticated header value straight to `WebhookMetadata`.

### Proof of Concept
1. Attacker signs up for the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Attacker creates an order on their own store, capturing the resulting raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed by Shopify using the app's shared `client_secret`).
3. Attacker sends a direct HTTP POST to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, so `HmacValidator.validate` passes), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` validates the HMAC successfully (it only checks `B`/`H`) and dispatches to the handler with `shop: "victim-shop.myshopify.com"`, causing the host app to process attacker-controlled order data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
