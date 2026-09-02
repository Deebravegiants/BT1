I have enough evidence to finalize the analysis.

### Title
Webhook shop identity is trusted from an HMAC-unauthenticated header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` used to route/process a webhook from the `X-Shopify-Shop-Domain` header, but the HMAC signature that `Registry.process` validates only covers the raw request body, never the shop header. Since Shopify apps share a single `client_secret` (and thus the same HMAC key) across every merchant that has installed the app, a valid `hmac`+`body` pair obtained from a webhook delivered to the attacker's own shop can be replayed with a different `Shop-Domain` header to make the app believe the payload originated from a victim shop.

### Finding Description
The equality the gem should enforce is: `shop bound by hmac == shop acted upon`. Instead:

- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC computed by `HmacValidator.compute_signature` binds only the JSON body bytes to the app's `client_secret` — it says nothing about which shop sent the request.
- `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the body or any signed value [2](#0-1) .
- `Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., body integrity) and then immediately trusts `request.shop` to build `WebhookMetadata`, which is handed to the host application's handler as the tenant identifier [3](#0-2) .
- `HmacValidator.validate` computes the signature using the single, shop-independent `Context.api_secret_key` (or `old_api_secret_key`) [4](#0-3) . This is the same secret for every shop that installed the app.

Because the secret is shared across tenants and the header is unsigned, an attacker who controls a shop that has installed the target app can capture one of their own legitimate webhook deliveries (valid `body` + valid `hmac`, both computed with the shared `client_secret`) and resend that exact `body`/`hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still pass because it only checks `body` against `hmac`; `Registry.process` will then dispatch the payload to the handler tagged with the attacker-chosen `shop`, causing the host app to store or act on attacker data under (or query/return data for) the wrong tenant.

This is the same root-cause shape as the report's "field acted upon but not covered by the cryptographic check": in `PendlePTOracle` a decimal factor is used in a computation without being properly bound/validated to the exponent the code assumes; here, the tenant identifier used downstream is used in a security decision (which shop's data this event pertains to) without being bound to the value the HMAC actually authenticates.

### Impact Explanation
This breaks the tenant boundary the whole `shopify_api` webhook subsystem is meant to enforce: any bytes signed as `(client_secret, body)` for one tenant are treated as fully authenticated for whatever `shop` header rides along with them. A malicious merchant of the app can trigger cross-tenant data confusion/injection in any downstream logic that trusts `WebhookMetadata#shop` as the record owner — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only that the attacker run their own Shopify store with the target app installed (a normal, unprivileged merchant relationship, not owner/admin credentials of the app) and be able to POST to the app's public webhook endpoint with modified headers, which is standard capability of any HTTP client — no `api_secret_key`, access token, or other Shopify-controlled secret is required.

### Recommendation
Bind the shop identity into the value that is HMAC-verified — e.g., include the `shop-domain` header (and `topic`/`webhook-id`) as part of `Request#to_signable_string`, or independently verify that the shop domain embedded in the JSON body payload (present for topics like `shop/redact`) matches the header value before trusting `Request#shop`, rejecting the webhook when they diverge.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and subscribes to a webhook topic.
2. Shopify delivers a webhook to the app with a legitimate `body` and `X-Shopify-Hmac-SHA256` header computed from the app's shared `client_secret`.
3. Attacker captures this `body`/`hmac` pair and replays it to the app's webhook endpoint, replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the signature over `@raw_body` and succeeds because the body and hmac are unchanged and the shared secret is the same [5](#0-4) .
5. `request.shop` returns `"victim.myshopify.com"` [2](#0-1) , and the handler receives `WebhookMetadata` claiming the (attacker-controlled) payload belongs to the victim shop [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
