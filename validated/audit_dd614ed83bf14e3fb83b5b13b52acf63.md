### Title
Webhook shop/topic identity not covered by HMAC signature allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers and passed unchecked to the app's webhook handler. Because the HMAC only binds the body bytes, not the shop/topic identity, a party who has obtained one valid `(body, hmac)` pair (for example from a webhook fired to their own shop's endpoint) can present that same signature with a different `shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic.

### Finding Description
`Registry.process` verifies authenticity solely via: [1](#0-0) 

The HMAC check calls into `Utils::HmacValidator.validate`, which validates against `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all sourced from HTTP headers that are never included in the signed content: [4](#0-3) 

`Registry.process` then dispatches the handler using the *unauthenticated* `request.shop` and `request.topic` values as the trusted tenant/topic identity: [1](#0-0) 

The broken binding, stated as an equality that the code fails to enforce:
`HMAC-verified(raw_body)` == `identity used by handler (shop, topic)` — in reality the code only proves `HMAC-verified(raw_body)`, and `shop`/`topic` are accepted from headers with no cryptographic tie to the signature. Any caller in possession of one legitimate `(raw_body, x-shopify-hmac-sha256)` pair — trivially obtainable by installing the app on their own shop and capturing a real webhook delivery — can resend that exact body/signature to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` and `x-shopify-topic` header. `Registry.process` will pass HMAC validation and invoke the handler believing the event legitimately originates from the spoofed shop/topic.

### Impact Explanation
This breaks the tenant identity binding relied upon by any host application: the webhook handler receives `WebhookMetadata` with an attacker-chosen `shop` while the cryptographic proof only covers the body bytes. For topics whose bodies are small/fixed or attacker-influenced (e.g., mandatory topics such as `customers/redact`, `shop/redact`, or `app/uninstalled`, whose payload structure is minimal and predictable), an attacker who is a legitimate merchant of the app can replay their own valid signature while claiming to be a different shop, causing the host application to execute shop-scoped side effects (data deletion/redaction, uninstall handling, session/token cleanup) against a victim tenant they do not control. This is a cross-tenant impact caused directly by a gem-level identity-binding gap.

### Likelihood Explanation
The attacker only needs to be a normal, unprivileged user of the app (install it on any shop to receive one genuine webhook delivery with a valid HMAC) — no `api_secret_key`, access token, or privileged account is required. Replaying the captured request to the app's public webhook endpoint with a modified `shop-domain`/`topic` header is straightforward with any HTTP client.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed/verified content (or independently verify that the `shop` header corresponds to a shop that is actually subscribed to the given `webhook_id`/topic) before dispatching to the handler, rather than trusting header values whose authenticity is not covered by the HMAC.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com` and trigger a webhook for a topic with a small/predictable body (e.g. `app/uninstalled`), capturing the raw body `B` and header `x-shopify-hmac-sha256: H`.
2. Send a POST to the victim app's webhook endpoint with:
   - `raw_body = B`
   - `x-shopify-hmac-sha256 = H`
   - `x-shopify-shop-domain = victim-shop.myshopify.com`
   - `x-shopify-topic = app/uninstalled`
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` using `to_signable_string` (`raw_body` only), which succeeds because `B`/`H` are a genuinely matching pair.
4. The handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the signature never proved anything about that shop, resulting in the host app processing a cross-tenant event as if it came from the victim shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
