### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the raw request body against the `X-Shopify-Hmac-Sha256` header, but the `shop` value that is handed to the application's webhook handler as the tenant identifier is read from a separate, unsigned header. Because the app's webhook secret (`Context.api_secret_key`) is shared across *all* shops that install the app, any unprivileged attacker who installs the app on their own store can capture a validly-signed webhook (body + HMAC) and replay it against the same public webhook endpoint with the `shop-domain` header changed to a victim shop, producing a request that passes HMAC validation but is attributed to the wrong tenant.

### Finding Description
The `Request` object's signable content is only the raw HTTP body: [1](#0-0) [2](#0-1) 

`shop` is derived independently from the `shop-domain` header and is not part of `to_signable_string`: [3](#0-2) 

`Registry.process` validates authenticity using `HmacValidator.validate`, which only checks `verifiable_query.to_signable_string` (the body) against the HMAC: [4](#0-3) [5](#0-4) 

Once the body's HMAC passes, `request.shop` (the unauthenticated header value) is forwarded unchanged as the tenant identity into `WebhookMetadata`, which the host application's handler uses to decide which shop's data to act on: [6](#0-5) 

The equality the library implicitly claims to guarantee is:
`hmac_valid(body) == (body, shop) originated together from Shopify for that shop`

but what it actually verifies is only:
`hmac_valid(body) == body was signed with the app's secret at some point (for any shop)`

Since the webhook secret is per-app (not per-shop), any shop that has installed the app — including one created by an attacker for free — can generate a legitimately-signed `(body, hmac)` pair. The attacker can then submit that exact pair directly to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header for a victim shop's domain. `HmacValidator.validate` will still succeed because it never inspects the shop header, and `Registry.process` will invoke the handler believing the event came from the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding that host applications rely on when processing webhooks (e.g., `app/uninstalled`, data-deletion, or entitlement-changing topics keyed by `shop`). An attacker can cause the application to process attacker-supplied, HMAC-"valid" webhook data under a victim shop's identity, leading to cross-tenant data confusion or state corruption — a Critical-class impact (cross-tenant access) as defined by the scope of this exercise.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-controlled development/trial store (a normal, unprivileged action any developer can perform), (2) receiving one legitimately signed webhook payload from Shopify for a topic with body content that is either empty or attacker-influenced, and (3) sending an HTTP POST directly to the app's public webhook endpoint with the captured body/HMAC and a forged shop-domain header. No secrets, tokens, or privileged access are required, making this readily reachable by any unprivileged internet user who can install the target app.

### Recommendation
Bind the shop identity to the signed content instead of trusting an unsigned header:
- Verify that the shop reported in the header is actually associated with the specific webhook delivery by cross-checking it against Shopify's `X-Shopify-Webhook-Id` via an authoritative source (e.g., re-fetching/confirming registration ownership), or
- Include the shop domain (and topic) as part of the material verified by the HMAC comparison where the app's webhook processing distinguishes behavior per shop, and reject any request whose header-derived identity cannot be corroborated.
- At minimum, document/log that `Registry.process`'s shop attribution is unauthenticated and cannot be trusted for tenant-differentiating business logic without additional verification by the host application.

### Proof of Concept
1. Attacker creates a free development store and installs the target Shopify app, becoming a legitimate (but unprivileged, low-trust) merchant of that app.
2. Attacker triggers (or waits for) a webhook delivery for a topic with a predictable/attacker-controlled body (e.g., an empty-body or generically-shaped topic) to their own endpoint/proxy, capturing the raw body and the `X-Shopify-Hmac-Sha256` value Shopify computed using the app's single, shared `api_secret_key`.
3. Attacker crafts a new HTTP POST to the target application's public webhook endpoint using:
   - the exact same raw body,
   - the exact same `X-Shopify-Hmac-Sha256` value,
   - `X-Shopify-Topic` optionally set to whichever topic they want handled,
   - `X-Shopify-Shop-Domain` set to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over the body and succeeds because it matches; `request.shop` returns `victim-shop.myshopify.com` unchecked and is passed to the handler, causing the application to execute tenant-scoped logic (e.g. deletion, deactivation) against the victim shop using attacker-controlled webhook content.

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
