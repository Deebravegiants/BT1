### Title
Webhook shop-domain/topic identity not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from unauthenticated HTTP headers, while `to_signable_string` (the value the HMAC actually protects) is only the raw request body. `Utils::HmacValidator.validate` only checks that the body's HMAC matches, then `Registry.process` trusts the header-derived `shop`/`topic` to route and construct `WebhookMetadata` passed to the app's handler. The identity binding "HMAC-verified bytes == bytes acted upon" is broken: the shop tenant that the app acts on behalf of is never part of the verified payload.

### Finding Description [1](#0-0) 

- `hmac` is computed/read from the `hmac-sha256` header.
- `to_signable_string` returns only `@raw_body` — line 37.
- `shop`, `topic`, `webhook_id`, `api_version` are all read straight from request headers (lines 15-32) and are **not** included in `to_signable_string`.

`Utils::HmacValidator.validate` verifies only that `HMAC(secret, raw_body)` matches the received signature: [2](#0-1) 

`Registry.process` gates entirely on this body-only check, then forwards the unverified `request.shop` / `request.topic` to the handler: [3](#0-2) 

Because the HMAC never binds to the `shop-domain` (or `topic`/`webhook-id`) header, any request whose body+HMAC pair is valid for the shared secret will pass validation regardless of which `shop-domain` header value is sent. An unprivileged internet user who can obtain (or predict) one valid `(raw_body, hmac)` pair for the app's `client_secret` — e.g., by installing the app on a shop they control and capturing a real webhook delivery (bodies are frequently small/predictable, e.g. `"{}"` as used in the gem's own tests) — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (and `shopify-topic`) for a victim shop. The equality the gem should enforce is:

`shop_that_HMAC_authenticates == shop_the_handler_acts_on`

but the gem instead enforces only `HMAC(body) == received_hmac`, with `shop` sourced from an entirely separate, unauthenticated channel (HTTP header).

### Impact Explanation
This crosses a tenant boundary: `WebhookMetadata.shop` is the value host applications typically use to look up the merchant's session/access token and to scope side effects (data updates, notifications, uninstall/GDPR handling, etc.). Since the gem-provided webhook dispatch guarantees only "some request was actually signed by the app's secret" rather than "this request is authentically about shop X," an attacker who is a legitimate merchant in one shop can forge webhook deliveries that the app processes as belonging to a different, victim shop — a cross-tenant confusion primitive that this scan's rules classify as Critical-tier (cross-tenant access) if a host application relies on `data.shop`/`data.topic` from this gem without additional out-of-band verification.

### Likelihood Explanation
The attacker needs no privileged credentials, access token, or the app's `client_secret` — only the ability to become a merchant/install the app on any single shop (the normal, expected, unprivileged path for any Shopify app) in order to legitimately receive one real webhook and capture its `(raw_body, hmac)` pair, then replay it directly to the app's public webhook endpoint with a forged `shop-domain` header. This requires no host-application misconfiguration; it is a property of the verification logic implemented entirely inside this gem (`Request#to_signable_string`, `HmacValidator.validate`, `Registry.process`).

### Recommendation
Bind the tenant identity into what is cryptographically verified, or explicitly cross-check it after verification:
- At minimum, `Registry.process` (or `Request`) should require the caller to supply the expected `shop` (e.g., from an already-authenticated session/webhook registration record keyed by shop) and assert `request.shop == expected_shop` before invoking the handler, rather than trusting the header value implicitly.
- Document prominently that `shop`, `topic`, and `webhook_id` returned by `Request` are **not** covered by the HMAC and must not be treated as authenticated identifiers on their own; callers must independently correlate them (e.g., against known installed shops) before acting.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (a normal, unprivileged onboarding flow) and lets Shopify deliver a real webhook, e.g. `orders/create` with body `"{}"` and a valid `shopify-hmac-sha256` header — the attacker now possesses a `(raw_body="{}", hmac=H)` pair that is valid for the app's `client_secret`.
2. Attacker sends a raw POST directly to the app's public webhook endpoint with:
   - `raw_body = "{}"`
   - `shopify-hmac-sha256: H` (captured value)
   - `shopify-topic: orders/create`
   - `shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `shopify-webhook-id: <anything>`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, "{}") == H` — this passes because the body/HMAC pair is genuinely valid for this app's secret. [4](#0-3) 
4. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {}, ...)`, and any host-application logic keyed on `data.shop` now executes as though this event genuinely originated from `victim-shop.myshopify.com`, despite the HMAC never having verified that binding.

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
