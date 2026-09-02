Confirmed root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while the tenant-identifying `shop` field is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . `Registry.process` validates the HMAC over the body only, then forwards `request.shop` straight to the app's handler as the authoritative tenant identity [3](#0-2) .

### Title
Webhook `shop` (tenant identity) header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC signature solely over the raw request body, but derives the tenant-identifying `shop` (and `topic`/`webhook_id`) values from HTTP headers that are entirely outside the signed payload. `Webhooks::Registry.process` trusts this unauthenticated `shop` value and passes it directly to the app's webhook handler as `WebhookMetadata#shop`, breaking the intended binding between "the shop whose HMAC was verified" and "the shop the handler believes the payload belongs to."

### Finding Description
`HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac` [4](#0-3) . For webhooks, `to_signable_string` is defined as just the raw body bytes [1](#0-0) , and `hmac` is parsed from the `hmac-sha256` header [5](#0-4) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read from other, unsigned headers [6](#0-5) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body vs. secret) before dispatching to the handler with `shop: request.shop` taken verbatim from the header [3](#0-2) . There is no cross-check that the `shop-domain` header actually corresponds to the shop whose data appears in the signed body, nor any comparison against a shop recorded at webhook-registration time.

The broken identity binding is: `shop authenticated by HMAC == shop delivered to handler`. In reality, only the body bytes are authenticated; `shop` is asserted, not proven.

Any entity capable of sending an HTTP POST to the app's webhook endpoint with a body+HMAC pair that is valid for *some* shop (e.g., an attacker's own Shopify development store, which legitimately receives real signed webhooks from Shopify for events on that store) can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header naming a victim merchant. Because the header is unauthenticated, `HmacValidator.validate` still returns `true` (the body signature is untouched), and `Registry.process` forwards `shop: <victim-shop>` to the handler alongside the attacker-controlled body content.

### Impact Explanation
Applications built on this gem commonly key persistence, authorization, or business logic in their webhook handlers off `WebhookMetadata#shop` (e.g., "look up the merchant record for this shop and update it using the payload"). Because `shop` is not bound to the HMAC-verified body, an attacker can cause the app to process (and persist) attacker-controlled payload content under a victim merchant's identity — a cross-tenant data integrity/confidentiality violation delivered through the gem's own webhook-verification API.

### Likelihood Explanation
Likelihood is high for any app that has at least one legitimate webhook subscription (the attacker needs one instance of a genuinely-signed body/HMAC pair for any topic, which the attacker can obtain trivially from their own installed development store) and exposes its webhook endpoint publicly, which is required for Shopify's own webhook delivery to work. No access token, `client_secret`, or privileged account is required — only the app's public webhook URL and one real webhook delivery to any store the attacker controls.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the signed payload verification, or independently verify that the `shop-domain` header matches a shop for which the specific `webhook_id`/subscription was registered, before constructing `WebhookMetadata` in `Registry.process`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted as a tenant boundary without additional server-side verification (e.g., looking up the installation record independent of the header).

### Proof of Concept
1. App registers a webhook subscription and receives a legitimate webhook from Shopify for `attacker-shop.myshopify.com`, e.g.:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <valid HMAC of raw_body under app's client_secret>
   shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id":1,...attacker-controlled order payload...}
   ```
2. Attacker captures this exact `raw_body` and `hmac-sha256` header value (trivial, since it is delivered to the app's own webhook endpoint, which the attacker can also observe by controlling the receiving infra for their own store, or simply by controlling the body content of the order they place in their own store).
3. Attacker resends the identical body and `hmac-sha256` header, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` re-computes the HMAC over the (unchanged) body and finds it valid, since the header is never part of `to_signable_string`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker payload>, ...)` to the app's handler, which processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
