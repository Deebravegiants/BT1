## Title
Webhook Shop and Topic Attribution Bypass via Unsigned Headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, while the `shop` and `topic` values used to route and process the webhook are read from HTTP headers that are **not covered by the signature**. Any unprivileged actor who can install the app on their own shop (or otherwise obtain one legitimately-signed webhook body/HMAC pair) can replay that same body/HMAC with forged `shopify-shop-domain` and `shopify-topic` headers, passing HMAC validation while causing the host app to attribute and process the event as belonging to a different, victim, shop and/or a different topic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from headers that are excluded from that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the request, then immediately trusts `request.topic` and `request.shop` to route to a handler and construct the `WebhookMetadata` passed to app code: [3](#0-2) 

`Utils::HmacValidator.validate` only proves that `secret` produced `computed_signature` for `to_signable_string` (i.e., the raw body) — it says nothing about which shop or topic header accompanied that body: [4](#0-3) 

The identity binding the gem implicitly relies on is:
`shop signed-for (in the HMAC-covered bytes) == shop the handler is told about (request.shop)`

That equality does not hold here: the HMAC only binds the body bytes, and `shop`/`topic` are parsed from unauthenticated headers. Because the webhook signing secret is the app's single shared `api_secret_key` (used across every shop that installs the app), any shop that installs the app receives real webhooks with a valid HMAC over some body. That installer (an unprivileged actor, requiring no special credentials) can capture one such `(body, hmac)` pair and replay it to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header value and/or `shopify-topic` header value. `HmacValidator.validate` still succeeds because it only checks the body/HMAC pair, and `Registry.process` then invokes the handler believing the event came from whatever shop/topic the attacker put in the headers.

### Impact Explanation
This breaks the tenant boundary the webhook API is supposed to enforce: an app that keys any behavior (data lookups, session retrieval, side effects like uninstall handling, order/customer sync, etc.) off `WebhookMetadata#shop` can be made to act on/for a different merchant's identifier while the actual signed payload originated from the attacker's own shop. This is a cross-tenant confusion vulnerability reachable by any user able to install the app on a shop they control, satisfying the "cross-tenant access" high/critical impact criteria.

### Likelihood Explanation
Likelihood is high: installing an app is an unprivileged action available to any Shopify user, webhook endpoints are public HTTP endpoints by design, and forging arbitrary headers on an HTTP request requires no special tooling. The only constraint is that the attacker must supply a body that was actually HMAC-signed by the shared secret — trivially satisfied by using one of their own shop's real webhook deliveries (e.g., an `app/uninstalled` or generic low-content-body event) and swapping only the `shopify-shop-domain`/`shopify-topic` headers.

### Recommendation
Include `shop`, `topic` (and ideally `api_version`/`webhook_id`) in the HMAC-covered signable content, or otherwise cryptographically bind them to the body (e.g., compute the signature over a canonical string containing body + these header values) inside `Webhooks::Request#to_signable_string`, so `HmacValidator.validate` cannot succeed unless the shop/topic attribution matches what was actually signed by Shopify for that specific delivery.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. body `{}` with headers `shopify-hmac-sha256: <valid-hmac-of-{}-with-shared-secret>`, `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: some/topic`.
2. Replay a POST to the app's webhook endpoint with the identical body `{}` and identical `shopify-hmac-sha256` value, but set `shopify-shop-domain: victim.myshopify.com` (and optionally a different `shopify-topic`).
3. `Utils::HmacValidator.validate` (called from `Webhooks::Registry.process`, see `lib/shopify_api/webhooks/registry.rb:190`) recomputes HMAC over `@raw_body` only and it matches, so validation passes.
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: {}, ...)` — the app processes the event as if it came from the victim shop, even though only the attacker's shop ever produced a signed payload.

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
