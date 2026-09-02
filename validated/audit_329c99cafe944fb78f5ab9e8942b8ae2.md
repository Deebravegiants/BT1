### Title
Webhook shop identity not covered by HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body alone, while the `shop`, `topic`, and `webhook_id` values used downstream by `Registry.process` are read directly, unauthenticated, from HTTP headers. Because the HMAC never binds the `shop` header to the verified bytes, any request whose *body* carries a valid signature will be accepted regardless of which shop the `shop-domain` header claims to be from, breaking the binding `HMAC-verified(raw_body) == {shop, topic, webhook_id}` that the handler implicitly relies on.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id`, however, are pulled straight from headers with no cryptographic tie to the signed body: [2](#0-1) 

`Registry.process` verifies only the HMAC of the body, then dispatches the handler using the unauthenticated `request.shop` value as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` in turn only checks `verifiable_query.to_signable_string` (the raw body, in the webhook case) against the app's secret: [4](#0-3) 

Because `shop-domain` is never part of the signed material, an unprivileged internet user who legitimately installs the app on their own store will receive genuine, correctly-HMAC'd webhook deliveries from Shopify for their own shop. They can capture one such delivery and replay it to the app's public webhook endpoint while swapping only the `X-Shopify-Shop-Domain` header to a victim shop's domain and, if desired, the `X-Shopify-Topic`/`X-Shopify-Webhook-Id` headers as well. The HMAC check still passes (it only re-hashes the untouched raw body with the app's own secret, which was never disclosed to the attacker — it's simply the same body Shopify already signed for the attacker's own shop). `Registry.process` then invokes the registered handler with `WebhookMetadata.shop` set to the victim's domain, so any host application that uses this `shop` value to look up/act on tenant data (mark a shop uninstalled, process an order webhook, trigger GDPR-style redaction, etc.) is now doing so for the wrong tenant — this is a cross-tenant boundary crossing produced entirely by this gem's identity binding.

### Impact Explanation
This is a cross-tenant access primitive: an attacker who controls no more than their own installed shop instance can cause the app to treat forged tenant-attributed webhook events as if they originated from a different, victim shop, without ever needing the app's `api_secret_key`, an access token, or any privileged credential. Depending on the handler logic wired up by the host application (which is exactly the intended, documented use of `Registry.process`/`WebhookMetadata#shop`), this can corrupt or falsely mutate another merchant's data path — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any app exposing a shared public webhook endpoint (the standard integration pattern documented for this gem): the attacker only needs to install the target app on a shop they control, capture one real webhook delivery, and resend it to the same endpoint with a modified `shop-domain` header — no secret material, brute forcing, or privileged access is required.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` headers in the HMAC-signable string (or otherwise cryptographically bind them to the verified payload), so that a webhook payload's declared shop cannot be altered independently of its signature. At minimum, `Registry.process` should cross-check `request.shop` against a shop already known/authorized for the `webhook_id` before dispatching to handlers.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; wait for Shopify to deliver a real webhook, e.g. `orders/create`, with headers:
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - raw body `B`.
2. Replay the exact same body `B` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb) recomputes the HMAC over `B` only and finds it matches — the request is accepted.
4. `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host application to process attacker-controlled webhook content under the victim shop's identity.

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
