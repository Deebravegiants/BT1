### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#shop` (and `topic`, `webhook_id`, `api_version`) are read directly from unauthenticated HTTP headers, while the HMAC signature verified by `Utils::HmacValidator.validate` only covers the raw request body (`to_signable_string` returns `@raw_body`). The `shop` attribute is passed straight through to the handler as the tenant identifier for the delivered webhook, without that identifier ever being included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; the `hmac` itself is read from the `hmac-sha256` header, and `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate, unsigned headers: [3](#0-2) 

After the HMAC check passes, `request.shop` is forwarded verbatim to the app's handler as the authoritative tenant identifier: [4](#0-3) 

The identity binding that should hold is: `shop-that-produced-the-signed-body == shop-delivered-to-handler`. In this implementation that equality is never enforced — the signature only proves "this body byte-string was HMAC'd with the app's client secret at some point," it says nothing about which shop the body belongs to. Any request whose body was legitimately signed for shop A (e.g., a webhook the attacker's own store, which is a real installed tenant of the app, legitimately received) can be replayed with the `shopify-shop-domain` header rewritten to shop B, and it will still pass `HmacValidator.validate` because the header is not part of `to_signable_string`.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged attacker who controls one legitimate installation of the app (their own dev/test store) can capture their own valid `(raw_body, hmac)` pairs and replay them to the app's public webhook endpoint with a forged `shopify-shop-domain`/`x-shopify-shop-domain` header naming a victim shop. The handler in the host app trusts `WebhookMetadata#shop` as the tenant scope for whatever action the webhook triggers (e.g., updating shop-scoped local state, marking a shop uninstalled on `app/uninstalled`, clearing shop configuration, enqueuing shop-scoped jobs) — see the documented handler contract that explicitly treats `data.shop` as "The shop domain of the webhook":

Since the request passes `Registry.process`'s only authenticity check, the library itself provides no way for a correctly-implemented handler to distinguish a genuine webhook for shop B from a replayed one for shop A wearing shop B's header. This crosses a tenant boundary using only the app's own signing secret (never the victim's credentials), satisfying the "cross-tenant access" bar for a High/Critical-class finding.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app on a shop they control (which is the normal, unprivileged path to becoming an app "merchant") and then capture at least one legitimate webhook delivery's raw body and HMAC for that shop. No secrets, tokens, or victim cooperation are needed — only the ability to receive one webhook from their own tenant and to send an HTTP POST to the app's public webhook route with a modified header.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is authenticated, or otherwise re-derive the shop identity from data that is cryptographically tied to the signed body rather than from a sibling header. Concretely:
- Extend `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to include the `shop`, `topic`, and `webhook_id` header values (e.g., a canonical concatenation) so `HmacValidator.validate` fails if any of these are altered relative to what Shopify signed.
- If Shopify's own HMAC scheme only ever signs the body, document (and enforce in `Registry.process`) an additional invariant: the caller must independently confirm that `request.shop` corresponds to a shop for which this specific webhook subscription (`webhook_id`) was registered, before trusting `data.shop` in the handler.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; receive a legitimate webhook delivery, e.g.:
   - Headers: `shopify-topic: app/uninstalled`, `shopify-hmac-sha256: <valid-hmac-of-body>`, `shopify-shop-domain: attacker.myshopify.com`
   - Body: `{}`
2. Replay the exact same body and `shopify-hmac-sha256` value to the same webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(..., @raw_body)` against the header HMAC — this still matches because `@raw_body` is untouched: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim.myshopify.com", ...)`, and any shop-scoped side effect the host app performs (e.g., disabling `victim.myshopify.com`'s integration) is triggered by the attacker without ever holding credentials for `victim.myshopify.com`.

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
