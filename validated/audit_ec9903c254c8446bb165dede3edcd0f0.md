## Title
Webhook shop domain header is not covered by the HMAC signature, allowing shop-attribution spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw request body only. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers and are never included in the signed payload, yet `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the authenticated tenant identity for dispatching the webhook to handlers.

### Finding Description
`Utils::HmacValidator.validate` verifies a request by recomputing an HMAC over `verifiable_query.to_signable_string` and comparing it to the `hmac` field with `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight out of unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates only the body-based HMAC and then dispatches to the handler using the unauthenticated `request.shop` and `request.topic` values: [3](#0-2) 

This breaks the identity binding the host application relies on: `shop attributed to webhook payload == shop that Shopify actually signed the payload for`. Because the signature is computed purely from the raw body and the shared `api_secret_key`, the *same* valid HMAC remains valid regardless of which `shopify-shop-domain` (or `shopify-topic`/`shopify-webhook-id`) header value accompanies it. An attacker who can obtain one genuinely-signed webhook body — for example by having the app installed on a shop they control and receiving their own legitimately-signed webhook deliveries — can replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (body untouched), so `Registry.process` calls the handler with `WebhookMetadata` claiming the victim shop as the source: [4](#0-3) 

Any host application logic that keys off `WebhookMetadata#shop` to select a tenant's session, access token, or database record will act on attacker-supplied data under a spoofed shop identity.

### Impact Explanation
This is a Critical-tier cross-tenant issue: an unprivileged internet actor with only legitimate access to their own shop's webhook stream can forge the shop-domain attribution on a request that still passes this gem's own HMAC check, causing the host application to process attacker-controlled webhook data as if it originated from a different merchant's shop.

### Likelihood Explanation
Requires the attacker to possess at least one validly-signed webhook body (trivial — install the app on any shop they control, which triggers real signed webhook deliveries), then replay it with a modified `shopify-shop-domain`/`shopify-topic` header to the app's public webhook endpoint. No secret key or credential theft is required, only observation of the gem's documented but incomplete signature scope.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material — or otherwise cryptographically bind them to the body — rather than trusting them as bare, unauthenticated headers in `ShopifyAPI::Webhooks::Request#to_signable_string`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimately delivered webhook request, e.g. `orders/create`, with headers `shopify-hmac-sha256: <valid_hmac>`, `shopify-shop-domain: attacker.myshopify.com`, and raw body `B`.
2. Replay the exact same request to the app's webhook endpoint, replacing only the header `shopify-shop-domain: victim.myshopify.com` (and, if desired, `shopify-topic`).
3. `ShopifyAPI::Utils::HmacValidator.validate` still succeeds because it only recomputes HMAC over the unchanged raw body `B`: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"` and body `B`, even though Shopify never sent this payload for `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
