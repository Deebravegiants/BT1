### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then reads the `shop`, `topic`, and `webhook_id` fields from HTTP headers that are never included in the signed material and hands them to the app's handler as trusted identity data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are all pulled straight from headers, none of which are part of the signable string: [2](#0-1) 

`Registry.process` validates only the HMAC over the body and then trusts `request.shop` (header-derived) when constructing the data passed to the app's handler: [3](#0-2) 

The equality this breaks is: `shop authenticated by Shopify's signature (the entity whose secret produced the HMAC over the body)` != `shop asserted in the x-shopify-shop-domain header consumed by the handler`. Since the HMAC never binds the shop identifier (or topic/webhook-id) to the signed bytes, any request carrying a *previously valid* `(body, hmac)` pair — for instance a webhook payload the attacker's own shop legitimately received, or one captured via a debugging proxy/log — can be replayed with the `x-shopify-shop-domain` header rewritten to point at an arbitrary victim shop. `HmacValidator.validate` will still pass because it only recomputes the signature over `@raw_body`: [4](#0-3) 

The forged request is accepted as authentic and routed to the registered handler with an attacker-chosen `shop` value, exactly the "field acted on but not covered by the HMAC" identity-binding break the review is looking for.

### Impact Explanation
If the host application's webhook handler uses `data.shop` (as constructed here) to look up a session/access token, update per-tenant records, or otherwise act on behalf of "the shop", an attacker who can obtain any one valid `(body, hmac)` pair (e.g., from their own installed app instance, from webhook logs, or from a network capture) can spoof events attributed to a different, victim shop. This enables cross-tenant data confusion/injection of fabricated events for a shop the attacker does not control, without possessing that shop's or the app's credentials — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP POST to the app's public webhook endpoint with a body+HMAC pair that was valid for *any* shop (trivially obtainable by installing the app on an attacker-controlled shop and capturing its own legitimate webhook) plus control over the `x-shopify-shop-domain` (or legacy `X-Shopify-Shop-Domain`) header, which any unprivileged internet user sending raw HTTP requests can set. No secrets, tokens, or privileged access are required.

### Recommendation
Bind the shop (and ideally topic/webhook-id) identifier into the signed material actually verified, or require the caller to independently confirm that the header-derived `shop` corresponds to a shop with an active session/installation before trusting it in the handler. At minimum, document and enforce that `WebhookMetadata#shop` must be cross-checked against the app's own session store keyed by an independently-established tenant identity before being used for any authorization-sensitive decision.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture one legitimate webhook delivery, e.g. `orders/create`, noting the raw body `B` and the `x-shopify-hmac-sha256` header value `H` (valid for `B` against the app's shared secret).
2. Send a new POST to the app's webhook endpoint with the same body `B` and header `H`, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `B` only and succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-22`), so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the request was never sent by Shopify for `victim.myshopify.com`.

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
