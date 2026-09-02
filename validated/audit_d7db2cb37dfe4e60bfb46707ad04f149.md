### Title
Webhook HMAC only covers the request body, not the `shop`/`topic` headers, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `topic`, `shop`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers and are never included in the HMAC-signed material. `ShopifyAPI::Webhooks::Registry.process` trusts these header-derived fields (in particular `shop`) and hands them to the host application's handler as soon as `Utils::HmacValidator.validate` succeeds on the body alone.

### Finding Description
The identity binding that should hold is:
`shop header used by the handler == shop that the HMAC actually authenticates`

`Request#to_signable_string` breaks this equality: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are parsed purely from headers, with no cryptographic binding to the body they're paired with: [2](#0-1) 

`HmacValidator.validate` computes the signature exclusively from `to_signable_string` (i.e. the raw body) and the app secret: [3](#0-2) 

`Registry.process` raises only if the body-only HMAC fails, then immediately forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` values to the app's handler: [4](#0-3) 

Because the signature is a deterministic function of `(raw_body, api_secret_key)` only, the exact same `(raw_body, hmac)` pair remains valid no matter what `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers accompany it. Any entity capable of receiving one legitimately-signed webhook (e.g., by installing the merchant's public app on their own store, which requires no special privilege and no knowledge of `api_secret_key`) can capture that valid `(body, hmac)` pair and resend it to the app's webhook endpoint with an attacker-chosen `shopify-shop-domain` header. `Utils::HmacValidator.validate` will still return `true`, and `Registry.process` will dispatch the payload to the handler tagged with the attacker-chosen shop, topic, and webhook id.

### Impact Explanation
This breaks the tenant identity binding at the heart of the webhook trust model: the library gives the host application no reliable signal linking `data.shop` to the actual signed content. An application that uses `WebhookMetadata#shop` (as documented/intended) to decide which merchant's records to create/update/delete based on the webhook body can be made to apply another shop's or an attacker-fabricated shop's webhook body to an arbitrary target shop identifier, i.e. cross-tenant data confusion/injection using only a replayed valid signature. This matches the Critical "cross-tenant access" impact category, since the merchant-identifying field is never authenticated even though the gem treats a successful `HmacValidator.validate` as proof that the *whole webhook*, including its shop attribution, is legitimate.

### Likelihood Explanation
Likelihood is limited by: (1) the attacker must first obtain at least one legitimately-signed `(body, hmac)` pair, which is possible for any user who can install the target app on any Shopify store (including a free/dev store they control) and capture their own webhook deliveries; (2) the impact depends on the host application trusting `WebhookMetadata#shop`/`#topic` to scope its side effects, which is the standard, documented usage pattern for this gem's webhook registry. Given how straightforward it is to obtain a valid signed body (self-installation, no secrets needed) and how central `shop` is to any multi-tenant webhook handler, exploitability is realistic despite not being a "day one" bypass of the secret itself.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material — e.g. by having `to_signable_string` canonicalize headers + body — or otherwise cryptographically bind them (such as verifying `shop` against session/install state maintained by the host app) before dispatching to handlers, rather than relying purely on a body-only HMAC to vouch for out-of-band header values.

### Proof of Concept
1. Install the target app (which uses this gem's `ShopifyAPI::Webhooks::Registry`) on an attacker-controlled store `attacker-shop.myshopify.com` and register/trigger a webhook subscription (e.g., `orders/create`).
2. Capture the legitimately delivered webhook: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this validates via `HmacValidator.validate` per [1](#0-0) .
3. Replay a POST to the app's webhook endpoint reusing the exact same body `B` and header `H`, but set `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`/`shopify-webhook-id`).
4. `Utils::HmacValidator.validate` still returns `true` because only `B` is hashed, per [3](#0-2) ; `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` and the attacker's body `B`, per [4](#0-3) , causing the host app to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
