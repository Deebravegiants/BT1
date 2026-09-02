### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-spoofed webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the shop identity (`shop-domain` header) is read separately and never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then dispatches the handler using the unauthenticated `shop` header value as the tenant identifier. This mirrors the reported bug class: a value used to determine tenant/identity ("field acted on") is not covered by the authentication check ("HMAC").

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string` and `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers and are not part of the signed content at all: [2](#0-1) 

`Registry.process` validates only that the body's HMAC is a genuine Shopify signature, and then trusts the header-derived `shop` value verbatim when constructing the metadata passed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`shop authenticated by the HMAC == shop used as the tenant key passed to the handler`

In reality, no shop identity is bound by the HMAC at all — the signature only proves "this body came from Shopify for *some* shop", not "this body came from Shopify for *this* shop." Because `shop-domain` is excluded from the signed string, the two sides of the binding are independent: the signature is valid for the body regardless of which shop header accompanies it.

### Impact Explanation
Any internet user who has legitimately received at least one real webhook from Shopify (e.g., by installing the target app, or any app, on their own trial/dev store) possesses a genuine `(raw_body, hmac)` pair signed with the app's `client_secret`. They can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` / `shopify-shop-domain` header value. `HmacValidator.validate` will pass (the body's signature is still valid), and `Registry.process` will hand the app's `WebhookHandler` a `WebhookMetadata` claiming the body belongs to the attacker-chosen victim shop: [4](#0-3) 

Any downstream logic that uses `data.shop` as a tenant/session key (e.g., to look up `Session`, update per-shop records, or trigger per-shop side effects) will act on the victim shop's identity using attacker-controlled data, i.e. cross-tenant data corruption/processing.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus one legitimately signed `(body, hmac)` pair, which is obtainable without any privileged credentials (e.g., by using one's own free/dev Shopify store to receive real webhook deliveries for whatever topic is targeted). No access token, `client_secret`, or session data is needed.

### Recommendation
Bind the shop identity into the signed material that `HmacValidator` verifies for webhooks (e.g., include the `shop-domain` header, or otherwise cryptographically bind the header set to the body before computing/comparing the HMAC), so a genuine signature for shop A's payload cannot be replayed under shop B's identity.

### Proof of Concept
1. Attacker creates/owns a Shopify dev/trial store and installs an app (any app) that uses this gem, receiving a genuine webhook delivery with a valid `x-shopify-hmac-sha256` for a known `raw_body`.
2. Attacker sends a POST to the target app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain` to the victim's `myshopify.com` domain.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC.
4. `handler.handle` is invoked with `WebhookMetadata#shop` equal to the attacker-supplied victim domain, causing the app to process attacker-controlled webhook content under the victim tenant's identity.

### Citations

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
