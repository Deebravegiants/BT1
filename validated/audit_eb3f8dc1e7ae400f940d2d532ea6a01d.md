### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted for tenant identification but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body. The `shop-domain` header, which is the only tenant identifier passed to the app's webhook handler, is never included in the signed material. Any actor who can obtain one valid `(body, hmac)` pair for the configured `client_secret` — trivially available to any merchant/developer who has the app installed on their own store — can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and the library will accept it as an authentic webhook for that arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers: [1](#0-0) 

But the value that is actually HMAC-verified is only the raw body: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature purely against `to_signable_string` (i.e. `@raw_body`), with no header input: [3](#0-2) 

`Registry.process` uses this HMAC check as its sole authenticity gate, then immediately forwards `request.shop` — an unauthenticated header value — to the app's handler as the tenant identity for the event: [4](#0-3) 

Because the signature never binds to `shop-domain`, `topic`, `webhook-id`, or `api-version`, any `(raw_body, hmac)` pair valid for the app's `client_secret` remains valid no matter what those header values are changed to. This breaks the identity binding `hmac-verified-request == webhook-for-shop-in-headers`: the HMAC only proves "some webhook signed with this app's secret," not "this webhook belongs to `shop-domain: X`."

### Impact Explanation
An attacker who installs the app on their own (attacker-controlled) shop can trigger any webhook topic they choose (e.g. `app/uninstalled`, `customers/data_request`, `shop/update`, or any custom topic the app subscribes to) and capture the resulting `raw_body` + `x-shopify-hmac-sha256` pair — both of which are visible to them as the receiving app owner/operator of the endpoint, or interceptable since nothing about them is shop-specific beyond the body content. They can then re-POST that exact body and HMAC to the app's webhook endpoint with `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) rewritten to name a victim shop. `Registry.process` will validate the HMAC successfully and hand the handler a `WebhookMetadata` claiming the event is `shop: victim-shop.myshopify.com`, causing the app to act on/record data for the wrong tenant — a cross-tenant identity-confusion condition (e.g. false uninstall/data-erasure processing, incorrect state transitions, poisoning per-shop caches/records keyed by `request.shop`).

### Likelihood Explanation
Obtaining a valid `(body, hmac)` pair requires no special privilege beyond installing the app on any shop (including a free/attacker-controlled development store) and triggering an event that the app subscribes to — well within reach of an unprivileged internet user with normal Shopify Partner/dev access. The replay itself is a single unauthenticated HTTP POST to the app's public webhook endpoint using library-processed headers exactly as documented in `docs/usage/webhooks.md`.

### Recommendation
Bind the tenant identity into the verified material instead of trusting a bare header:
- Sign/verify a canonical string that includes `shop-domain` (and ideally `topic`/`webhook-id`) alongside the body, not just the raw body, or
- Require callers of `Registry.process` to pass the expected `shop` (from their own trusted install/session store) and have the registry assert `request.shop == expected_shop` before dispatching to the handler, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host application against a known/installed shop list before being trusted for any tenant-scoped action.

### Proof of Concept
1. Install the target app on an attacker-controlled development store `attacker-shop.myshopify.com`.
2. Trigger a subscribed webhook topic (e.g. `app/uninstalled`) so Shopify sends a real webhook with a valid `x-shopify-hmac-sha256` for the app's `client_secret` and body `B`.
3. Capture `B` and its HMAC value `H` (visible from the app's own logs/inbound request, since the attacker controls the receiving deployment or can intercept their own traffic).
4. Replay to the same endpoint:
```
POST /webhooks HTTP/1.1
x-shopify-topic: app/uninstalled
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim-shop.myshopify.com
x-shopify-webhook-id: <any>
x-shopify-api-version: 2024-01

B
```
5. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (it only checks `B` against `H`), and `Registry.process` dispatches the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", ...)`, causing the app to treat this as an authentic event for `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
