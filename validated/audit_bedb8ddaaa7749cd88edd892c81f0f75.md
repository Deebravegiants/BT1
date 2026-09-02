## Title
Webhook `shop`, `topic`, and other identity headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The bug report flags a Solidity contract for accepting parallel arrays without checking that their lengths match, which lets attacker-supplied data be misaligned/misattributed relative to trusted data. The structural analog in this gem is `ShopifyAPI::Webhooks::Request`: the HMAC signature only covers the JSON body, while the identity-critical `shop`, `topic`, `webhook-id`, and `api-version` fields are read straight from unauthenticated HTTP headers and handed to the webhook handler unmodified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC exclusively against that string: [1](#0-0) [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, which are never part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the handler using `request.shop` from the unauthenticated header: [4](#0-3) 

This is precisely the "field acted on but not covered by the HMAC" pattern: the equality the code implicitly assumes is `shop_header == shop_that_actually_generated(raw_body)`, but nothing enforces that binding. An attacker who has legitimately received one webhook delivery for their own shop (a valid `(raw_body, hmac)` pair, obtainable by installing the app on any shop they control) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a victim shop's domain. `HmacValidator.validate` will still pass, since it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the victim shop, delivering the attacker's own webhook body under the victim tenant's identity.

### Impact Explanation
This breaks the identity binding between the HMAC-authenticated payload and the shop/topic the host application uses to route and persist that payload. Host applications built on this gem's documented contract (`Registry.process` -> handler receives `WebhookMetadata#shop`) reasonably trust that field as originating from Shopify for that shop, since HMAC validation just occurred. An attacker can use this to inject/attribute data cross-tenant (e.g., causing order/webhook data for their own shop to be recorded, or handler logic re-executed, under a victim's shop record), which falls under cross-tenant access.

### Likelihood Explanation
Exploitation requires only that the attacker control a shop that installs the app (trivial for any Shopify Partner/dev store) to obtain one valid `(body, hmac)` pair for a chosen webhook topic, plus the ability to POST to the app's public webhook endpoint with custom headers, no access to `api_secret_key` or any privileged credential is needed. The header substitution is straightforward HTTP manipulation.

### Recommendation
Bind the identity-critical webhook metadata into the signed material, or otherwise independently verify it, e.g., include `shop`/`topic` in the value passed to `HmacValidator.validate`/`to_signable_string`, or require host applications to cross-check `request.shop` against a shop that is independently known to be associated with the specific `webhook_id`/subscription before trusting it. At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated and must not be trusted for authorization decisions without additional verification (e.g., matching against a registered shop's known webhook subscriptions).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook, capturing the raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` using the app's `api_secret_key`, which the attacker never sees but doesn't need to).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only compares `H` against the HMAC of `B`: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)`, i.e., the app processes attacker-controlled data as if it came from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
