Based on the report's core theme (data accepted from an unauthenticated field allows bypassing an identity binding), the closest analog in this gem is in the webhook processing path.

## Title
Webhook Shop/Topic Headers Are Not Covered by HMAC, Enabling Cross-Tenant Webhook Replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the HMAC-over-body, then dispatches the handler using the unauthenticated `shop` value, binding attacker-influenceable header data to a tenant identity that the signature never covered.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which in turn calls `validate_signature`, computing the HMAC strictly over `to_signable_string` (the body) and comparing it to the `hmac` header: [3](#0-2) [4](#0-3) 

After that check passes, the handler is invoked with `shop: request.shop` taken from the unauthenticated header, and the host application typically uses this value to look up/attribute the tenant session: [5](#0-4) 

The binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic)`, so that `shop` is cryptographically tied to the payload that produced a valid signature. Instead the actual binding enforced is only `hmac == HMAC(secret, body)`, leaving `shop` (and `topic`) fully attacker-controlled at the header level once *any* valid `(body, hmac)` pair is known.

### Impact Explanation
An unprivileged internet user can install the target app on their own Shopify development/trial store (a legitimate, self-service action requiring no special privilege) and thereby receive genuine, correctly-HMAC-signed webhook deliveries for their own shop. Because the HMAC covers only the JSON body, the attacker can capture one such valid `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain. `Registry.process` will accept it as valid (body signature checks out) and hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop. Any host application that uses `data.shop` to select the tenant record to update (the standard, documented usage pattern) will process attacker-supplied body content under the victim's tenant identity — a cross-tenant data-integrity/confusion vulnerability that requires no credentials beyond ordinary self-serve app installation.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented webhook-processing pattern (dispatch handler keyed by `data.shop`), since obtaining a legitimate `(body, hmac)` pair only requires installing the app once on an attacker-owned store, and replaying it is a single crafted HTTP request with modified headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable content (or otherwise cryptographically bind them, e.g. by re-deriving/confirming the shop via a separate authenticated channel such as querying Shopify with the associated session/access token) so header values cannot be swapped independently of the signed body.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a shop they legitimately own.
2. Shopify sends a webhook to the app with a valid `x-shopify-hmac-sha256` for the JSON body and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this `(raw_body, hmac)` pair and replays the same HTTP request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate`, which recomputes the HMAC over `raw_body` only and matches, so no `InvalidWebhookError` is raised: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled body, and the host app processes/persists it as data belonging to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
