### Title
Webhook shop/topic identity spoofing via unsigned headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop` and `topic` values parsed from HTTP headers to route and attribute an incoming webhook, while `Utils::HmacValidator` only authenticates the raw request body. Because the HMAC signature does not cover the `shop-domain` or `topic` headers, an attacker who can obtain one valid `(raw_body, hmac)` pair (e.g., by installing the app on their own store and capturing a legitimately delivered webhook) can replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, causing the app to process attacker-controlled data as if it originated from a different, victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are separately parsed from headers and are never part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` compares `verifiable_query.hmac` against a signature computed solely from `to_signable_string` (i.e., the raw body), using `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.topic` and `request.shop` — values that were never part of the authenticated payload — to route to a handler and to build the `WebhookMetadata` passed into application logic: [4](#0-3) 

This breaks the intended identity binding: `hmac_valid ⇒ (body, shop, topic) all authentic`. In reality `hmac_valid` only proves `body` is authentic; `shop` and `topic` are attacker-controlled headers on any direct POST to the app's public webhook endpoint (the same endpoint Shopify itself posts to). An unprivileged internet user who has captured any one valid `(raw_body, hmac)` pair — trivially obtainable by installing the target app on their own store and triggering a webhook, no `api_secret_key` or victim credentials required — can resend that exact body/HMAC combination with a forged `x-shopify-shop-domain` header naming a different, victim shop. `Registry.process` will pass validation and hand the handler a `WebhookMetadata` claiming the data came from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: the gem authenticates bytes (the body) but the application-facing API surface (`WebhookMetadata#shop`, `#topic`) exposes unauthenticated, attacker-controlled values as if they were verified. Any host application that uses `request.shop`/`data.shop` to select per-tenant records, credentials, or database rows (the documented and expected usage pattern) can be made to act on the wrong tenant's data, since the library itself provides no signal distinguishing a genuine header from a forged one post-HMAC-check.

### Likelihood Explanation
Webhook endpoints are public HTTP endpoints reachable by anyone on the internet, matching Shopify's own webhook delivery model. Obtaining one valid `(body, hmac)` pair requires only installing the target app on an attacker-owned development/trial store (no special privilege) and capturing a single webhook delivery — a low-effort, unprivileged action.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verified content used by `HmacValidator`, or otherwise cryptographically bind them to the verified body (e.g., verify shop domain against the session/shop the app expects for that install, and validate the API version/topic against an allow-list tied to the verified body). At minimum, document that `shop`/`topic` are not authenticated by `HmacValidator.validate` and must be independently verified by the host application against known/installed shop records before being trusted.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and triggers any webhook (e.g. products/create), capturing:
raw_body = '{"id":1,...}'                 # exact bytes as delivered
hmac     = "<valid-x-shopify-hmac-sha256-from-capture>"

# 2. Attacker POSTs directly to the app's public webhook endpoint,
#    replaying the exact body/hmac pair but forging the shop header:
headers = {
  "x-shopify-topic"        => "products/create",
  "x-shopify-hmac-sha256"  => hmac,          # unchanged, still matches raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id"   => "attacker-controlled",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because it only checks raw_body,
# so the handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# even though the payload never originated from that shop.
```

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
