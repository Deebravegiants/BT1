### Title
Webhook `shop-domain` (and `topic`, `webhook-id`) header is trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), the `topic`, and the `webhook_id` entirely from unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only verifies the raw request body against the `X-Shopify-Hmac-Sha256` header. The shop-to-payload binding that the app relies on to route/act on a webhook for the correct merchant is never checked.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` - it does not include `shop`, `topic`, or `webhook_id`: [3](#0-2) 

Yet `shop`, `topic`, and `webhook_id` are read straight from attacker-controllable HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) and passed on unmodified to the app's handler as the tenant identity for the event: [4](#0-3) [1](#0-0) 

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` (and `host`, `state`, `code`, `timestamp`) *is* part of `to_signable_string` and therefore is bound by the HMAC: [5](#0-4) 

This is the exact bug class from the external report generalized to this gem: an identity field (`shop`) that the downstream code acts on (routing/tenant identification) is not covered by the integrity check (HMAC) that is supposed to authenticate the whole message. The equality the code should enforce is:

`hmac == HMAC(secret, canonical_representation_including(shop, topic, body))`

but what is actually enforced is:

`hmac == HMAC(secret, body_only)`, while `request.shop` is trusted unconditionally by `WebhookMetadata`/the handler.

### Impact Explanation
Because all merchants of a given app share the same `client_secret`/HMAC key, any body+HMAC pair that is valid for one shop's webhook is also a valid HMAC for the identical body claimed to originate from a different shop, since `shop` is not part of the signed content. An attacker who controls or observes a legitimately signed webhook delivery for their own shop (or replays a captured one) can resend it to the app's public webhook endpoint with a modified `shopify-shop-domain` header naming a victim shop, and the HMAC check will still pass. The handler then processes the (attacker-influenced) event data under the victim shop's identity - a cross-tenant data-integrity/identity confusion. Depending on what the app does with webhook data (e.g., `customers/data_request`, `customers/redact`, `shop/redact`, `app/uninstalled`, or business webhooks that trigger data mutation keyed by `shop`), this can lead to state corruption or actions taken against the wrong tenant, i.e., cross-tenant impact.

### Likelihood Explanation
Exploitation requires the attacker to have at least one validly-signed webhook body+HMAC pair, which is trivial to obtain by installing the app on the attacker's own (possibly free/dev) store and receiving a real webhook, or by using any topic whose body content the attacker can influence. No possession of `api_secret_key` is required. The webhook endpoint is a public HTTP endpoint by design, so the request is fully reachable by an unprivileged internet user.

### Recommendation
Include `shop`, `topic`, and any other headers the app relies on for routing/tenant identity in the HMAC-signed canonical string (or otherwise cryptographically bind them, mirroring how `AuthQuery#to_signable_string` binds `shop`/`host`). At minimum, document/enforce that consumers of `Webhooks::Request` must not treat `request.shop`/`request.topic` as authenticated unless they are independently verified (e.g., cross-checked against the session/shop the webhook was registered for), and consider validating the `shop` domain format and correlating it with an active, registered session before dispatching to handlers.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g., `orders/create`) so Shopify sends a POST with a legitimately computed `X-Shopify-Hmac-Sha256` for the raw JSON body `B`.
2. Capture the raw body `B` and the valid `hmac` header value `H = HMAC-SHA256(client_secret, B)`.
3. Replay a POST to the app's webhook endpoint with the same body `B` and same `hmac` header `H`, but set `shopify-shop-domain: victim.myshopify.com` (and reuse or omit `webhook-id`/leave `topic` as-is).
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)`, which still equals `H`, so validation succeeds: [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata` using `request.shop` (`victim.myshopify.com`) even though the payload actually originated from and was signed for `attacker.myshopify.com`: [7](#0-6) 
6. The app's handler acts on data for `victim.myshopify.com` using attacker-supplied `body`, achieving cross-tenant identity confusion without ever knowing the app's `client_secret`.

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
