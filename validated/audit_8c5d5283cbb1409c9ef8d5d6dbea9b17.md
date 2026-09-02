## Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`) values that the handler subsequently trusts and acts on are taken from HTTP headers that are **not** part of the signed material. Any party capable of triggering one legitimate webhook for their own shop can capture the `(raw_body, hmac)` pair and replay it against the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to a victim shop, and the request will still pass HMAC validation.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates only that HMAC: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, i.e. the raw body only, and never incorporates the `shop` header: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the webhook (request.shop, passed to the handler)` == `shop that Shopify actually generated the HMAC for`.

Because the HMAC only covers `raw_body`, this equality is never checked — `request.shop` can be any value the caller places in the `X-Shopify-Shop-Domain` / `Shopify-Shop-Domain` header while the HMAC remains valid for that same, unrelated body. A merchant who has installed the app (an "unprivileged internet user" relative to other tenants) can trivially generate one authentic webhook for their own shop (e.g., by creating an order), capture the raw body and its valid `hmac-sha256` value from that delivery, then POST the identical body+HMAC to the app's public webhook endpoint while substituting the target shop's domain in the shop header. `Registry.process` will accept it and dispatch `WebhookMetadata.new(topic:, shop: request.shop, body: request.parsed_body, ...)` to the app's handler as if it were an authentic event for the victim shop.

### Impact Explanation
Any app logic keyed off `WebhookMetadata#shop` (order/customer/product sync, GDPR/compliance webhooks, billing events, data deletion, etc.) can be triggered for a shop the attacker does not control, using only a body/HMAC pair harvested from the attacker's own store. This is a cross-tenant integrity/confidentiality issue: actions or data intended to be scoped to one merchant's tenant get attributed to (and can pollute or corrupt) another merchant's tenant, satisfying the "Critical - cross-tenant access" bar.

### Likelihood Explanation
The attacker only needs to be a legitimate installer of the target app (any merchant, freely obtainable via Shopify's app installation flow) — no access to `api_secret_key`, access tokens, or the victim's credentials is required. Capturing a raw body + HMAC from one's own webhook delivery and replaying it with a modified header is trivial with any HTTP proxy.

### Recommendation
Bind the shop (and ideally topic) into the signed material verified by the gem, or require callers to independently verify `request.shop` against a shop known/authorized for that HMAC (e.g., look up the shop's own `client_secret`-independent identity, or require the host app to only trust `request.shop` after confirming it is an already-installed/authorized shop) rather than trusting a header that carries no cryptographic binding to the signature.

### Proof of Concept
1. Install the app on Shop A (attacker-controlled) and trigger a real webhook (e.g., `orders/create`) so Shopify delivers a request with a valid `X-Shopify-Hmac-Sha256` computed over the raw JSON body.
2. Capture the exact `raw_body` and `hmac-sha256` header value.
3. Replay:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <captured-valid-hmac>
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>
X-Shopify-Api-Version: <any>

<captured raw_body>
```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"`, `body: <attacker's own order data>`, causing the app to process this as an authentic event for a shop the attacker doesn't own.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
