## Title
Webhook shop identity is read from an unauthenticated header while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its webhook signature over the raw body only, while the `shop` (and `topic`) values that are handed to the application's webhook handler are read straight from HTTP headers that are never included in that signature. This is the same class of bug as the reported Morpho issue: a value that is *acted on* (the tenant/shop identity) is not the same value that is *covered* by the integrity check (the HMAC), so the two can be made to diverge.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`. The `shop` accessor, however, is taken directly from the `shop-domain` header and is never mixed into `to_signable_string`: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (raw body only) and compares it against the `hmac` header using the app's `api_secret_key`: [3](#0-2) [4](#0-3) 

Because the signature only binds the byte content of the request body, the `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers can be altered after a genuine webhook has been captured without invalidating the HMAC check. `Registry.process` then passes the attacker-controlled `request.shop` straight to the host application's handler as authoritative tenant identity:

```
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```

The binding that should hold is:
`shop value verified by HMAC == shop value delivered to the handler`

but in this code the left side is empty (no shop binding in `to_signable_string`) while the right side is attacker-controllable, so the equality is broken.

### Impact Explanation
Any party that can obtain one valid `(raw_body, hmac)` pair for the app's secret — trivially available to anyone who installs the app on their own store and receives a real webhook — can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` will still return `true` because it never looks at the header, so `Registry.process` will invoke the app's webhook handler believing the event originated from the victim shop. Any host application that uses `WebhookMetadata#shop` to select which tenant's data to update, delete, or resync (a common and documented use of this field) can be made to act on the wrong tenant, i.e., cross-tenant access/write using a spoofed identity — meeting the Critical, cross-tenant impact bar.

### Likelihood Explanation
The prerequisite is only the ability to receive one legitimately signed webhook (attacker's own shop can trivially generate one) and the ability to POST arbitrary headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged credential is required. This is reachable purely through documented use of `ShopifyAPI::Webhooks::Request` / `Registry.process` in this gem.

### Recommendation
Bind the tenant-identifying header(s) into the signed material, e.g. compute the HMAC over (or otherwise cryptographically bind) `shop-domain`, `topic`, and `webhook-id` in addition to the raw body, or independently verify that the `shop-domain` header matches a shop associated with the session/store the payload actually pertains to before invoking the handler. At minimum, document/require host apps to further authenticate `shop` rather than trusting the header as-is.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook delivery `POST /webhooks` with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac>`, and body `B`.
2. Replay the identical request but change only `X-Shopify-Shop-Domain` to `victim.myshopify.com`, keeping `B` and `X-Shopify-Hmac-Sha256` unchanged.
3. `ShopifyAPI::Webhooks::Request#hmac` still reads the same (still-valid) HMAC header; `to_signable_string` returns the unchanged `B`, so `Utils::HmacValidator.validate` returns `true`.
4. `Registry.process` dispatches to the handler with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload/HMAC were never produced for that shop.

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
