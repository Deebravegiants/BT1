Confirmed: `Registry.process` at [1](#0-0)  validates the HMAC via `Utils::HmacValidator.validate(request)`, but `Request#to_signable_string` only signs the raw body [2](#0-1) , while `request.topic`, `request.shop`, `request.api_version`, and `request.webhook_id` are all read straight from HTTP headers, unauthenticated by the signature [3](#0-2) . Those unsigned header values (in particular `shop`) are then handed directly to the app's handler as tenant-identifying metadata [4](#0-3) .

### Title
Webhook `shop`/`topic`/`webhook-id` headers are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string solely from the raw request body, never incorporating the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. `Registry.process` trusts `HmacValidator.validate(request)` as proof the whole request is authentic, then passes `request.shop`, `request.topic`, and `request.webhook_id` — none of which are HMAC-covered — on to the app's webhook handler as the tenant/event identity.

### Finding Description
The identity binding the gem is supposed to guarantee is: `hmac(raw_body) valid` ⟺ `(body, shop, topic, webhook_id) all authentic`. In reality the gem only proves `hmac(raw_body) valid` ⟺ `raw_body authentic`; the header fields are excluded from the signable string: [5](#0-4) 

`Registry.process` uses this validation result to authorize dispatch to a topic-specific handler and constructs `WebhookMetadata` directly from the same unsigned headers: [1](#0-0) 

Because `shop` is read via `shopify_header("shop-domain")` with no cryptographic tie to the signed body, any party capable of replaying a validly-signed body (for example a legitimate merchant/app-installer who receives real signed webhooks for their own store, or any component in the delivery path that can rewrite headers while forwarding the untouched body) can present the same `(raw_body, hmac)` pair together with a different `shopify-shop-domain` header. `HmacValidator.validate` will still return `true`, since it only recomputes `HMAC(raw_body)` and compares to the received signature — it never touches `shop`, `topic`, or `webhook-id`: [6](#0-5) 

The result is that the equality the app relies on — `verified_hmac == true` implies `shop field == the tenant that actually generated this event` — does not hold. The `shop` value is attacker-influenceable independent of the signature.

### Impact Explanation
This breaks the tenant boundary the webhook system is designed to enforce: `WebhookMetadata#shop` is the value host applications use to scope database writes, GDPR/redact processing, and other per-tenant side effects. An app receiving a webhook whose body legitimately belongs to shop A but whose `shop` header has been swapped to shop B will process shop A's real (signed) event data under shop B's identity, or vice versa — a cross-tenant data integrity/leak issue reachable without possessing `api_secret_key`, an access token, or any privileged credential. The same unsigned-header problem also applies to `topic` (can misroute a payload into a handler intended for a different event class) and `webhook_id` (breaks idempotency/dedup logic keyed on this value).

### Likelihood Explanation
Exploitation requires only the ability to deliver an HTTP POST to the app's webhook endpoint with a body+hmac pair that was legitimately produced by Shopify at some point (which the attacker, as any merchant with the app installed, can legitimately obtain for their own shop) and modified headers. No knowledge of `api_secret_key` is needed because the attacker is replaying an existing valid `(body, hmac)` pair rather than forging a new signature. This is a design gap in `Request#to_signable_string`, not a downstream misuse issue, since the gem's own validator does not check headers at all.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the raw body) in the value signed/verified by `HmacValidator`, or otherwise cryptographically bind these header fields to the body before trusting them in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Capture a legitimate signed webhook delivery for shop `a.myshopify.com`: `raw_body`, and header `shopify-hmac-sha256` computed by Shopify over that body.
2. Resend the identical `raw_body` and `shopify-hmac-sha256` value to the app's webhook endpoint, but replace the `shopify-shop-domain` header with `b.myshopify.com` (and/or change `shopify-topic`/`shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(raw_body)` and matches the untouched `hmac-sha256` header, returning `true`.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, using the attacker-supplied `shop-domain`/`topic`/`webhook-id` values even though the "verified" signature never covered them.

### Citations

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
