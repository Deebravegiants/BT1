### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are not covered by the HMAC signature, allowing cross-tenant attribution of a replayed webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively over that body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are read directly and passed unchecked into `WebhookMetadata`, which host applications use to attribute the webhook to a shop/tenant.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
The shop, topic, webhook id, and API version are parsed straight from headers with no cryptographic binding to the signed body: [2](#0-1) 
`HmacValidator.validate`/`validate_signature` compute the HMAC purely from `verifiable_query.to_signable_string`, i.e., the body: [3](#0-2) 
`Registry.process` only checks the HMAC of the body, then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight into the handler without any additional binding to the signed content: [4](#0-3) 
This is packaged into `WebhookMetadata`, whose `shop` field is a plain, unauthenticated `String`: [5](#0-4) 

The identity binding broken is: `HMAC-verified bytes (raw_body)` ≠ `shop identity trusted by the handler (header shop-domain)`. Since all shops that install the same app share one `api_secret_key`, any body+HMAC pair produced by a legitimate webhook delivery for shop A (e.g., an attacker's own store, which they can freely install the app on) remains a valid HMAC regardless of which `shop-domain` header value accompanies it. An attacker who controls the raw HTTP request to the app's webhook endpoint can therefore take a genuinely-signed `(body, hmac)` pair from their own store's webhook deliveries and resend it with the `shop-domain` header rewritten to a victim shop, and `Registry.process` will accept it and hand the handler a `WebhookMetadata` claiming it originated from the victim shop.

### Impact Explanation
If the host application relies on `WebhookMetadata#shop` (as returned by this gem, having already passed HMAC validation) to select tenant-scoped resources, session/store data, or the access token used for subsequent Admin API calls on behalf of "the shop that sent the webhook," an attacker can cause the app to act on/for an arbitrary victim shop using replayed, validly-signed webhook bytes they generated on their own store. This is a cross-tenant confusion at the boundary this gem is responsible for (the point where it converts a raw signed request into a trusted `shop` identity), matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop to obtain a genuine `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`, and (2) sending an HTTP request to the app's public webhook endpoint with that body/HMAC but an attacker-chosen `shop-domain` header. No access token, `client_secret`, or privileged account is needed beyond the ability to install the app on any store (which is the normal, unprivileged installation flow for public apps). This is a realistic, low-effort attack path.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind them to the verified payload, so that a body signed for one shop cannot be replayed and attributed to a different shop. At minimum, document that `WebhookMetadata#shop` is not authenticated against the signed bytes and must not be used as a sole tenant-identification input without additional server-side verification (e.g., cross-checking against a known/expected shop for that endpoint or webhook ID via the Admin API).

### Proof of Concept
1. Install the target Shopify app on attacker-owned store `attacker.myshopify.com`.
2. Capture a legitimately delivered webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — valid because `HmacValidator` only checks `H` against `B` per [1](#0-0) .
3. Replay the exact `(B, H)` pair to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds (it never inspects the shop header), per [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, per [7](#0-6) , causing the host app to process/attribute the (attacker-supplied) payload as if it came from the victim tenant.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
