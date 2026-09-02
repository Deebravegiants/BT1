This confirms the finding: the webhook HMAC only covers the raw body bytes, while the `shop`, `topic`, and `webhook-id` values that the handler uses to attribute the event to a tenant come from unauthenticated HTTP headers.

### Title
Webhook `shop` identity is trusted from an unauthenticated header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value read directly from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the digest against that signable string only [2](#0-1) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from caller-supplied headers with no cryptographic binding to the body or to the HMAC at all [3](#0-2) . `Registry.process` validates only the HMAC and then immediately trusts `request.shop`/`request.topic` to route and tag the event for the handler: [4](#0-3) .

This breaks the intended identity binding: `hmac_signed_bytes == raw_body` but the application-level equality it's implicitly relied upon to guarantee is `attributed_shop == raw_body_originating_shop`, which the code never checks. An unprivileged internet user who has ever seen one genuine webhook delivery for topic X on shop A (bodies for public/mandatory topics, or their own store's webhooks, are easy to obtain since Shopify sends the same `X-Shopify-Hmac-Sha256` value only as a function of body+secret, and the header/body pair is not otherwise bound together, so the same raw body + hmac can be replayed with a forged `X-Shopify-Shop-Domain` header) can send that exact `(body, hmac)` pair to the app's webhook endpoint with an arbitrary `shop-domain` header of their choosing. The HMAC validation passes because the body and secret are unchanged; the handler receives `WebhookMetadata` with the attacker-chosen `shop`, `webhook_id`, and `api_version` values [5](#0-4) .

### Impact Explanation
Because most real-world webhook handlers use the `shop` field to look up per-tenant records or trigger tenant-scoped side effects (e.g., "delete customer data for shop X", "disable shop X", "process order for shop X"), an attacker who can produce or intercept any one valid `(body, hmac)` pair can direct that payload's processing at a victim shop of their choosing by spoofing the `shop-domain` header — a cross-tenant confusion inside the app built on top of this gem's documented API. This matches the Critical bar for cross-tenant access, since the gem's own webhook-authentication primitive fails to bind the identity field the host application is expected to trust.

### Likelihood Explanation
Exploitability depends on the attacker obtaining at least one legitimate `(raw_body, hmac)` pair (e.g., from their own installed shop's webhook traffic, which they fully control and can capture) and being able to reach the app's public webhook endpoint, both of which require no leaked secrets, tokens, or privileged access — only normal use of the gem's webhook verification API as documented (`Registry.process`). This is a design gap in `HmacValidator`/`Webhooks::Request`, not a misuse of an undocumented API.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the verified body (e.g., verify `shop` against a known/allow-listed installation before dispatching), so that `to_signable_string` covers everything the handler is expected to trust, not just the body bytes.

### Proof of Concept
1. Register a handler for topic `orders/create` that looks up `data.shop` in local storage and performs a tenant-scoped action (per documented usage of `WebhookHandler#handle`).
2. As the owner of shop `attacker.myshopify.com`, install the app and capture one genuine webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`, independent of any shop header).
3. Replay: send a POST to the app's webhook endpoint with body `B` unchanged, `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `HmacValidator.validate` returns `true` (it only checks `H` against `B`) [6](#0-5) ; `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"` [7](#0-6) , causing the host application to act on the victim tenant using attacker-controlled body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
