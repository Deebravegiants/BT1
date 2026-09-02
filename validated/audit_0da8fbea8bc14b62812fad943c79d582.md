### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature check over the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed downstream by `ShopifyAPI::Webhooks::Registry.process` to select the handler and to build `WebhookMetadata`. Anyone who can produce one valid `(body, hmac)` pair — trivially achievable by installing the app on their own free/trial store and receiving a legitimate webhook — can replay that same body/hmac pair against the app's webhook endpoint with arbitrary `shop-domain`, `topic`, and `webhook-id` header values, since none of those fields are covered by the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the body: [2](#0-1) .

`Utils::HmacValidator.validate` verifies the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the raw body only: [3](#0-2) .

`Webhooks::Registry.process` validates only this body-bound HMAC, then dispatches using the unauthenticated `request.topic` to pick a handler, and forwards the unauthenticated `request.shop` straight into `WebhookMetadata` handed to the app's business logic: [4](#0-3) .

This breaks the identity-binding equality that the gem implicitly claims to guarantee: `hmac_valid(body) ⇒ shop_header == originating_shop`. In reality the gem only proves `hmac_valid(body)`; `shop_header` (and `topic`, `webhook_id`) float freely as attacker-controlled bytes that were "verified" for their signature but never "parsed" as part of what was signed — exactly the analog class of "bytes verified vs. bytes parsed" / "shop authenticated vs. shop used as identity key" called out in scope.

### Impact Explanation
An unprivileged internet user can install the target app on a store they control (no special privilege required — any Shopify Partner/dev store works), trigger a real webhook event, and capture the resulting `(raw_body, hmac)` pair Shopify sends. They can then replay that exact body and HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) headers with a victim tenant's domain. Because the signature check only validates the body, `Registry.process` accepts the forged request and hands the host application a `WebhookMetadata` claiming the payload originated from the victim shop. Any host application that trusts `WebhookMetadata#shop` to select which merchant's session/data to act on (the intended and documented use of this field) will act on the wrong tenant — a cross-tenant confusion/spoofing vector. This satisfies the Critical "cross-tenant access" impact bucket without requiring the app's `client_secret`, an access token, or any credential leak.

### Likelihood Explanation
Likelihood is High: the only prerequisite is the ability to install the target app once on any store (trivial for any developer/attacker) and to send arbitrary HTTP requests to the app's public webhook endpoint — both are unprivileged, unauthenticated-attacker capabilities. No secret key, token, or victim-side compromise is needed; only knowledge of the gem's header-parsing/signing scheme, which is public.

### Recommendation
Bind the identity-relevant headers into the signed material, or explicitly cross-check them against a source of truth:
1. Include `shop-domain`, `topic`, and `webhook_id` in the HMAC computation (e.g., concatenate them with the body before hashing, matching Shopify's actual webhook verification contract if it supports header-inclusive signing), or
2. If Shopify's webhook HMAC is defined as body-only by design, `Webhooks::Registry.process` must not treat `request.shop`/`request.topic` as authenticated identity for dispatch/metadata purposes without an additional binding check (e.g., verifying `shop` against a session already known for that specific webhook subscription ID, and rejecting if the webhook_id/shop pairing is inconsistent with what was registered).

### Proof of Concept
1. Install the target app on attacker-controlled dev store `attacker-shop.myshopify.com`; trigger an `orders/create` webhook and capture the raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or `X-Shopify-Topic: <different-topic>`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, B)` and compares to `H` — this passes because `B` is untouched: [5](#0-4) .
4. The handler for the spoofed topic is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, i.e. `shop = "victim-shop.myshopify.com"`, even though that request never actually originated from Shopify on behalf of that shop: [6](#0-5) .

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
