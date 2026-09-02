## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating the HMAC of the raw request body only. The `shop` (and `topic`, `webhook_id`, `api_version`) values that are handed to the app's handler and used to identify *which tenant* the payload belongs to are taken from HTTP headers that are never included in the signed material. This breaks the identity binding `hmac(signed_bytes) == hmac(bytes_the_handler_trusts_as_the_shop)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` show that only the raw JSON body is signed/verified: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` — i.e., that the body bytes match the HMAC — and then dispatches the handler using the unverified `request.shop`: [3](#0-2) 

`HmacValidator.validate` in turn calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` is exactly `@raw_body` — the header values (including `shop`) play no role in signature computation or verification: [4](#0-3) 

Because the app's `client_secret`/HMAC key is the same for every shop that installs the app, any unprivileged internet user who installs the app on their own (e.g., free-trial) store will legitimately receive a webhook body plus a valid HMAC signed with that shared secret. Since the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers are not part of the signed bytes, the attacker can resend the exact same body/HMAC pair to the merchant's public webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Registry.process` will still report `"Invalid webhook HMAC."`... no — it will pass validation (the body/HMAC pair is untouched and valid), and the handler will be invoked with `WebhookMetadata` whose `shop` is the attacker-chosen victim domain, even though the payload content actually belongs to the attacker's own shop.

This is the same class of defect as `UncmpPubKeyToCmpPubKey`: a value (`y`/`shop`) is trusted and passed downstream without checking that it is bound to the material that was actually authenticated (the curve equation / the HMAC).

### Impact Explanation
Any app that keys tenant-scoped writes off `WebhookMetadata#shop` (e.g., updating installation state, orders, inventory, or GDPR/compliance records identified by shop domain) can be made to apply attacker-supplied body content to a victim merchant's tenant record, since the shop identity used for authorization/dispatch is not bound to the authenticated bytes. This is a cross-tenant integrity issue reachable by any unprivileged internet user who can install the app on a shop they control.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-owned shop (freely available, e.g. a Shopify partner/dev store) to obtain one legitimately-HMAC-signed webhook body, and (2) replaying that body to the app's public webhook receiver endpoint with a modified `shop-domain` (or `X-Shopify-Shop-Domain`) header. No access to `api_secret_key`, tokens, or the victim's account is needed.

### Recommendation
Bind the shop (and topic/webhook id) identity to the authenticated material — e.g., include the relevant headers in the signed payload used for `to_signable_string`, or cross-check the shop header against a shop identifier embedded in the (currently unsigned) payload/session lookup before trusting it, so a valid HMAC for one shop cannot be replayed under another shop's identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` using the app's shared secret), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends `POST /webhooks` to the app with the identical body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC successfully (it only checks `B` against `H`) and invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
