## Analysis

The bug-class hint ("rounding causes state to diverge from what a check actually validates") maps most directly onto a genuine identity-binding gap in this gem's webhook processing: **the HMAC signature only covers the raw request body, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are taken from unauthenticated HTTP headers and are never included in the signed material.** [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the signature purely from `to_signable_string`, which for `Webhooks::Request` is `@raw_body`: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because every shop installing the same app shares the same `client_secret` (`Context.api_secret_key`), a valid HMAC for a payload produced by one shop's genuine webhook delivery is *also* a valid HMAC for that same payload when replayed with a different `shop-domain` header — the signature never binds shop identity to body content. This breaks the intended equality `shop_that_produced_and_signed_the_body == shop_reported_to_the_handler`.

### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against that body. The `shop`, `topic`, `api_version`, and `webhook_id` values consumed by `ShopifyAPI::Webhooks::Registry.process` and handed to the app's handler come from unauthenticated headers that are never part of the signed data.

### Finding Description
`Webhooks::Request#to_signable_string` is `@raw_body` [4](#0-3) , and `HmacValidator.validate_signature` compares `OpenSSL::HMAC.hexdigest(sha256, secret, signable_string)` against the received signature [5](#0-4) . Because the same `client_secret` is used for the shared app across all installing shops, any body+HMAC pair captured from a legitimate delivery to Shop A remains a byte-for-byte valid signature no matter what `shopify-shop-domain` header value accompanies it. `Registry.process` performs `Utils::HmacValidator.validate(request)` and, on success, forwards `request.shop` (parsed only from headers) directly to the handler without any additional binding check [3](#0-2) . An attacker who controls the delivery of the webhook request to the app's endpoint (e.g., a merchant who owns Shop A and can intercept/replay their own genuine webhook deliveries, since they legitimately receive a valid signed body/HMAC pair for their own shop) can resend that same body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header for Shop B. The signature check passes, and the app's webhook handler is invoked believing the data originated from Shop B, when it actually originated from Shop A.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook handlers: the `shop` field the gem asserts is safe to trust after signature validation is not actually bound to the signed content. Depending on how a host application uses `WebhookMetadata#shop` (e.g., to select which merchant's records to update, to look up per-shop tokens, or to trigger uninstall/GDPR flows), this enables cross-tenant data injection or state corruption in the host app driven entirely by a value never covered by the cryptographic check the gem exposes as its integrity guarantee.

### Likelihood Explanation
Requires only a party capable of delivering (or replaying) an HTTP request to the app's public webhook endpoint with a body+HMAC pair they legitimately received for their own shop, and no leaked secrets or elevated privileges are needed. Likelihood is bounded by the fact that the attacker needs a valid body/HMAC pair from *some* delivery of the same app (any shop they control receiving a webhook works), but no other credential is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material used for verification, or otherwise cryptographically tie the header-derived shop to the payload before trusting it — e.g., include the shop domain in `to_signable_string`, or independently verify via a signed field inside the JSON body rather than the header alone.

### Proof of Concept
1. App shop A installs the app and receives a legitimate webhook: body `B`, header `shopify-shop-domain: shop-a.myshopify.com`, valid `shopify-hmac-sha256` computed over `B` with the shared `client_secret`.
2. Attacker (owner/operator of shop A, or anyone able to capture that delivery) resends the exact same body `B` and HMAC to the app's webhook endpoint, but sets `shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `shop-b.myshopify.com` [6](#0-5) ; `HmacValidator.validate` succeeds because it only checks `B` against the shared secret [5](#0-4) .
4. `Registry.process` invokes the handler with `shop: "shop-b.myshopify.com"` and the body data that actually belongs to shop A [7](#0-6) , causing the host app to act on shop B's tenant context using shop A's data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
