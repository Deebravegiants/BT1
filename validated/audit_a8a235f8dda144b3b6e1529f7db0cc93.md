### Title
Webhook shop-domain/topic identity is not covered by the HMAC, enabling cross-tenant replay confusion - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity with an HMAC that covers **only the raw body bytes**, while the tenant-identifying `shop-domain` header (and the `topic`/`webhook_id`/`api_version` headers) are read directly from unauthenticated HTTP headers and handed to the app's handler as trusted identity. This breaks the intended binding `verified_bytes == acted_upon_identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC purely against `to_signable_string`: [2](#0-1) 

Yet `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled straight from HTTP headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then trusts `request.shop`/`request.topic` from headers to dispatch to a handler and to build the metadata the app acts on: [4](#0-3) 

This is the same class of bug as the reference finding: a value that is *acted on* (here, the shop identity/topic used to attribute and route a webhook event) is not part of the data actually covered by the integrity check (here, the HMAC signable string). In the reference report, funds were moved/frozen based on state (`getVaultChainIdOff`) that wasn't reconciled with the value actually used; here, the identity used to route/attribute an inbound event isn't reconciled with the bytes the signature actually protects.

An attacker who can capture (or is the recipient of, e.g. via a compromised/observing proxy, logging pipeline, or a shared network position) **one legitimately-signed webhook** for their own shop, or intercepts one destined elsewhere, can strip and replay it to the app's public webhook endpoint with the `shop-domain` header changed to an arbitrary shop, or the `topic` header changed to a different registered topic — the HMAC still validates because it only checks the untouched raw body, but the app will now process that body attributing it to a different shop or a different event type than the one it was actually signed/sent for. Since `api_secret_key` is a single shared secret across all of a given app's installs (not per-shop), any one captured, validly-signed webhook payload for the app is enough to forge the shop-domain binding for *any other* installed shop of that same app without ever needing the secret itself.

### Impact Explanation
This crosses the "cross-tenant access" boundary called out in scope: an app built on this gem's documented `Webhooks::Registry.process`/`WebhookHandler` API will process an event and attribute it (via `WebhookMetadata#shop`) to a shop that never actually sent/authorized that payload, since the gem provides no mechanism to bind the shop-domain header to the signed content. Downstream this can lead to data being written to the wrong tenant's records, redact/GDPR webhooks being spoofed against the wrong shop, or a handler for one topic firing on a payload actually generated for a different topic — all without possessing the app's `client_secret`.

### Likelihood Explanation
Requires an attacker to have captured at least one previously valid webhook delivery for the same app (any of its installed shops), which is a realistic scenario given webhooks traverse the open internet to a public endpoint, may be logged, proxied, or exposed via SSRF/log leakage in other components. No possession of `api_secret_key` or an access token is required — only replay of already-observed HMAC+body pairs with a substituted header.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload, so the HMAC check enforces `verified(shop, topic, body) == acted_upon(shop, topic, body)` rather than `verified(body) == acted_upon(shop, topic, body)`. At minimum, document loudly that these headers are unauthenticated and must not be trusted for tenant attribution without additional binding.

### Proof of Concept
1. App receives a legitimate webhook: `POST /webhooks` with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and some `raw_body`.
2. Attacker captures this exact request (e.g., via a logging proxy, shared reverse-proxy config, network capture, or the app's own request logs being exposed) — no secret key needed, just the wire bytes.
3. Attacker resends the identical `raw_body` and `hmac` header unchanged, but with `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes HMAC over `raw_body` (`Request#to_signable_string`) — the shop header is never part of the signed content: [1](#0-0) 
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `shop-b.myshopify.com`, so the app now believes shop-b sent the order/customer/redact event that actually belonged to shop-a: [5](#0-4)

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
