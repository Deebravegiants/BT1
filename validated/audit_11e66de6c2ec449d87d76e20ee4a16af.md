Based on my analysis, I found a valid analog to the reported bug class: an identity-critical field (`shop`, `topic`) that is *used* by the webhook dispatch logic but is *not covered* by the HMAC signature that authenticates the webhook request.

### Title
Webhook shop/topic identity not bound to HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` and `topic` HTTP headers to route and attribute the webhook to a specific merchant, exactly the "field acted on but not covered by the HMAC" pattern.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers, none of which are included in `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `hmac` against `to_signable_string` (i.e. the body), so it never covers `shop`/`topic`: [3](#0-2) 

`Registry.process` then dispatches to the handler using the *header-derived*, HMAC-unverified `request.shop` and `request.topic` as the merchant/tenant identity for the event: [4](#0-3) 

This breaks the intended binding: `shop-that-HMAC-authenticates == shop-that-handler-acts-on`. Since the webhook secret (`api_secret_key`) is a single per-app secret shared across every installed shop (not per-tenant), any unprivileged attacker who has legitimately installed the app on their own shop can capture one genuine webhook body+HMAC pair from Shopify, then replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with a victim shop's domain or a different topic. Because those headers are never part of the signed content, HMAC validation still succeeds, and the handler receives `WebhookMetadata` claiming the event came from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: it lets an attacker who controls a legitimate install make the app process forged events "as" an arbitrary target shop (e.g. triggering `shop/redact`, `customers/data_request`, `app/uninstalled`-style flows, or any custom handler logic keyed on `shop`), potentially causing the host application to take actions against, or leak data about, a shop the attacker does not control. This matches the Critical "cross-tenant access" impact class from the given criteria, since tenant identity here is entirely dictated by request headers with no cryptographic binding.

### Likelihood Explanation
Likelihood is High for any unprivileged internet user who can install the app once (a normal, permission-less action for a public Shopify app) to obtain one valid (body, HMAC) pair, then simply replay it with a modified `shop-domain`/`topic` header against the same public webhook endpoint — no access token, `api_secret_key`, or elevated privilege is required.

### Recommendation
Bind the shop/topic identity into what is authenticated: include `shop-domain` and `topic` (and any other header consumed by the handler) inside `to_signable_string`, or otherwise cryptographically bind them to the signed payload, so that `Utils::HmacValidator.validate` fails if any of these headers are altered relative to what the sender actually signed.

### Proof of Concept
1. Attacker installs the target app on their own shop (`attacker-shop.myshopify.com`), which is a normal unprivileged flow.
2. Shopify sends a legitimate webhook, e.g. `orders/create`, to the app with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`; attacker captures this request.
3. Attacker resends the identical body `B` and identical `X-Shopify-Hmac-Sha256` value, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` — unchanged — so validation passes: [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...)`, causing the app to process/act on data as if it originated from `victim-shop.myshopify.com`, despite the HMAC never having authenticated that shop identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
