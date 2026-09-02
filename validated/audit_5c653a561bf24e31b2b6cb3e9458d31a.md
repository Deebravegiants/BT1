The strongest reachable analog here is in the webhook signature verification path, not the OAuth/JWT flows (those correctly bind `shop`/`state` into the signed payload).

### Title
Webhook `shop`/`topic` identity not bound by HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never included in the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` trusts these unauthenticated header values once the body-only HMAC checks out, and hands them to the registered handler as the tenant identity.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the shared `api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC passes, then forwards the *unverified* `shop` and `topic` header values straight to the app's handler as the trusted tenant identity: [4](#0-3) 

The broken identity binding, as an equality that should hold but doesn't:
`bytes_verified_by_hmac (raw_body)` ≠ `identity_fields_acted_on (shop-domain header, topic header, webhook-id header, api-version header)`.

Because `api_secret_key` is a single app-level secret shared across every shop that installs the app (not a per-shop secret), any merchant who installs the app on their own store legitimately receives real webhook deliveries with a valid `(body, hmac)` pair for that secret. Since headers are excluded from the signed content, that same merchant (an unprivileged internet user with respect to any *other* tenant) can replay the untouched `body`/`hmac` pair to the app's public webhook endpoint while substituting `shopify-shop-domain` with a victim shop's domain and/or `shopify-topic` with any topic they choose (e.g. `app/uninstalled`, `shop/redact`). `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` calls the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` carrying the forged identity.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker who controls one shop's installation can make the app process events attributed to a completely different shop. Depending on the handler's logic (common patterns include deleting stored sessions/tokens on `app/uninstalled`, purging data on `shop/redact`, or writing order/customer state keyed by `shop`), this yields cross-tenant data corruption or forces state changes against a victim tenant with no access to that tenant's credentials — this is a cross-tenant access vulnerability (Critical), since the `shop` value is used downstream by consuming apps as an unauthenticated tenant identifier that the gem presents as verified.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (if adversarial) merchant of the app — no leaked secrets, no privileged account, no TLS interception. They only need one real webhook delivery to their own store (trivial to obtain by installing any app that registers webhooks) and the ability to POST an HTTP request with modified headers to the app's public callback URL.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content, or otherwise cryptographically bind them (e.g., derive them from a signed claim rather than raw headers), so `Utils::HmacValidator.validate` verifies the exact tenant/topic identity the handler receives — not just the body bytes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g., `orders/create`), capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed by Shopify with the app's shared `api_secret_key`).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with body `B` (unchanged), header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: app/uninstalled`.
3. `Utils::HmacValidator.validate` computes the HMAC over `B` only, matches `H`, and returns `true` — `Registry.process` proceeds and invokes the registered `app/uninstalled` handler with `shop: "victim-shop.myshopify.com"`, causing the app to treat the victim shop as having uninstalled (e.g., deleting its stored session/tokens) despite no action by the victim.

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
