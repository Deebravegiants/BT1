## Finding [1](#0-0) 

### Title
Webhook shop/topic/webhook-id attribution not covered by HMAC, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` binds `topic`, `shop`, `api_version`, and `webhook_id` directly to unauthenticated HTTP headers, while the HMAC signature that "proves" the request came from Shopify covers only the raw request body. `Registry.process` trusts these header-derived fields for tenant attribution after validating only the body's HMAC, breaking the intended identity binding: `verified(HMAC) = raw_body`, but `acted_upon = {raw_body, shop, topic, webhook_id}`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC solely against this signable string: [3](#0-2) 

`Registry.process` raises only if this body-only HMAC check fails, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` — all sourced straight from headers — to dispatch to the registered handler and construct `WebhookMetadata`: [4](#0-3) 

Because `shop-domain`, `topic`, and `webhook-id` are never part of the signed payload, any party who has observed one legitimate webhook delivery (body + valid HMAC for that body) — e.g., from their own shop, from a proxy/log, or from an app that logs raw webhook payloads — can resubmit the exact same body and HMAC to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `topic`, `webhook-id`) header. `HmacValidator.validate` will still return `true` because it never inspected the header values, and `Registry.process` will hand the attacker-chosen `shop` to the app's handler as if Shopify had reported that event for that shop. Handlers written per the library's own documented pattern (`data.shop`) will act on forged tenant attribution.

### Impact Explanation
This breaks the identity binding between "bytes verified" (raw body) and "bytes acted upon" (shop, topic, webhook_id), enabling cross-tenant webhook injection: an attacker can cause an app to process a webhook event as if it belongs to an arbitrary shop of their choosing, using only a previously observed legitimate webhook body/HMAC pair. Depending on the handler logic (which is written by app developers following this library's documented `data.shop` usage), this can lead to cross-tenant data corruption, state confusion, or triggering shop-scoped side effects (e.g., billing, order/inventory sync, uninstall handling) against the wrong tenant.

### Likelihood Explanation
No access to `api_secret_key` or any credential is required — the attacker only needs one previously delivered webhook body plus its accompanying `x-shopify-hmac-sha256` value, both of which are visible in transit/logs to anyone able to observe delivery to the app's public webhook endpoint (or via a compromised intermediary, browser extension, proxy, etc., on the recipient side), and the app's webhook URL must simply be reachable, which by design it is (Shopify webhooks are delivered over plain HTTPS POST to a public endpoint). This is a design gap in this gem's `Request`/`HmacValidator`, not a misuse of a documented API by the host app — the documented processing flow (`docs/usage/webhooks.md`) is exactly what `Registry.process` implements.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the verified body (e.g., verify a canonicalized string of `raw_body + headers` against the HMAC, matching how `Auth::Oauth::AuthQuery#to_signable_string` binds all OAuth callback fields into its signable string). At minimum, document that `shop`, `topic`, and `webhook_id` are unauthenticated and must not be trusted for tenant-scoped authorization decisions without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. App registers a webhook handler that trusts `data.shop` (per `docs/usage/webhooks.md` pattern) to look up/act on tenant-specific records.
2. Attacker observes (via logs, network capture, or by triggering a webhook to their own shop) one legitimate delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` under the app's `api_secret_key`), and `x-shopify-topic = T`.
3. Attacker sends a new POST to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain = victim-shop.myshopify.com` (a different shop than the one that actually triggered the original event).
4. `HmacValidator.validate` in [5](#0-4)  succeeds because it only checks `B` against `H`.
5. `Registry.process` in [4](#0-3)  invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the app to process the (forged) event as belonging to `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
