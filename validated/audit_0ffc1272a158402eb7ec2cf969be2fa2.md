Confirmed: `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . The `HmacValidator.validate` call in `Registry.process` only checks the HMAC against this signable string (the raw body) [3](#0-2) , so it never binds the `shop-domain` header to the signature. `Registry.process` then trusts `request.shop` as the tenant identity and forwards it straight to the handler [4](#0-3) .

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header values are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are never included in the signed payload. `ShopifyAPI::Utils::HmacValidator.validate`, invoked from `Registry.process`, therefore verifies only that the body bytes were signed with the app's secret — it does not verify which shop, topic, or webhook the signature was issued for.

### Finding Description
`Webhooks::Request` includes `Utils::VerifiableQuery` and implements:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` come straight from the `shopify-*`/`x-shopify-*` HTTP headers, which are attacker-controlled at the transport layer (any client can set arbitrary headers):
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [5](#0-4) 

`Registry.process` validates the HMAC over that signable string only, then uses `request.shop`/`request.topic` unauthenticated to build the metadata handed to the application's webhook handler:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [4](#0-3) 

The identity binding this breaks: `shop asserted in header == shop authenticated by HMAC`. In reality `HMAC(secret, raw_body)` is valid for *any* value of the `shop-domain`/`topic`/`webhook-id` headers, because those bytes are never part of the signed string. A merchant/attacker who has legitimately installed the app on their own shop receives real, correctly-signed webhooks from Shopify for that shop. They can capture one such webhook (valid `hmac-sha256` + `raw_body`) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to name a different shop/tenant that also uses the same app. `HmacValidator.validate` still returns `true` because it only checks the (unchanged) body against the (unchanged) HMAC — the header substitution is invisible to the check.

### Impact Explanation
If the host application (as documented/intended by this gem's `WebhookMetadata`/`Registry` contract) uses `data.shop` to select which merchant's tenant data to update (order status, fulfillment, GDPR redaction, inventory, etc.), an attacker can forge a webhook event that appears to originate from a shop they do not own, using only a webhook body they legitimately received for their own shop. This is a cross-tenant integrity/confidentiality violation driven purely by this gem's failure to bind the header-derived `shop` field to the HMAC it verifies.

### Likelihood Explanation
Any unprivileged internet user who can install the app on one shop (a normal, unprivileged action) can obtain a validly-signed webhook body/HMAC pair and replay it with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — this only requires the ability to receive one webhook for a shop the attacker legitimately controls and to make an HTTP POST with custom headers, both trivially available to any merchant/app installer.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values (and any other fields the application logic keys off of) inside the string that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., by only trusting `shop`/`topic` values that Shopify includes as part of the JSON body, or by having `Registry.process` independently confirm the claimed shop owns the given `webhook_id`/topic via API lookup before dispatching to the handler).

### Proof of Concept
1. App owner (attacker) installs the target app on `attacker-shop.myshopify.com` and lets it register a webhook for a topic they need (e.g., `orders/create`).
2. Shopify sends the app a real webhook: `raw_body = "{...attacker's order json...}"`, `x-shopify-hmac-sha256 = Base64(HMAC-SHA256(secret, raw_body))`, `x-shopify-shop-domain = "attacker-shop.myshopify.com"`.
3. Attacker captures this exact `raw_body` + `hmac-sha256` header, and replays the POST to the same webhook endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com` (a shop that also has the app installed).
4. `Webhooks::Request.new(raw_body:, headers:)` is built; `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, raw_body)`, which still matches, so validation passes: [3](#0-2) 
5. `Registry.process` dispatches `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` to the app's handler, which now processes attacker-controlled body data under the victim shop's tenant identity: [4](#0-3)

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
