The docs explicitly document `data.shop` as "the shop domain of the webhook", implying it's a trusted, verified value passed by `ShopifyAPI::Webhooks::Registry.process` to the handler — but the gem's own `Request#to_signable_string` only signs `@raw_body`, not the `shop-domain` header, so the "shop" field the handler acts on is never bound to the HMAC that `Registry.process` validates.### Title
Webhook `shop` field is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating that `HMAC(raw_body, api_secret_key)` matches the `X-Shopify-Hmac-SHA256` header, but the `shop` value that is subsequently handed to the application's webhook handler as the tenant identifier is taken from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never part of the signed material. This breaks the identity binding `HMAC-authenticated bytes == bytes the handler trusts as belonging to a specific shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only the raw body: [1](#0-0) 

Its `shop` accessor reads directly from an HTTP header with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e. over `raw_body` only via `to_signable_string`), and then immediately forwards `request.shop` to the application handler as the trusted tenant identifier, without any check binding `shop` to what was authenticated: [3](#0-2) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the body) and `verifiable_query.hmac` (the header value), never touching `shop`: [4](#0-3) 

The gem's own documentation instructs developers to treat `data.shop` from the handler as "the shop domain of the webhook" — an authenticated, trustworthy value — with no caveat that it is unauthenticated: [5](#0-4) 

Because a single `api_secret_key` is shared by the app across all shops that install it (there is no per-shop secret), any legitimate installer of the app can:
1. Trigger (or passively receive) a genuine webhook for their own shop, capturing the exact `raw_body` and its valid `X-Shopify-Hmac-SHA256` value.
2. Replay that identical body + HMAC to the app's webhook endpoint, but with the `X-Shopify-Shop-Domain` header rewritten to an arbitrary victim shop domain.
3. `HmacValidator.validate` still succeeds because the signed bytes (`raw_body`) are unchanged, yet `request.shop` — passed on to the handler — now points at the victim shop.

This is the same bug class as the `Lottery.lpDeposit` report: a value that the application acts on (`shop`, analogous to "active LP count") is not covered by the same authorization check/binding (`HMAC`, analogous to the `require` gate) that is supposed to guard the whole operation.

### Impact Explanation
If the host application's webhook handler uses `data.shop` to select which shop's records to update/create/redact (this is exactly the documented usage pattern, e.g., `shop/redact`, `customers/redact`, `customers/data_request` mandatory topics), an attacker-controlled shop can forge webhook events attributed to a shop it does not own. This is cross-tenant data injection/confusion, one of the specified Critical-severity outcomes ("cross-tenant access").

### Likelihood Explanation
The attack only requires an actor to install the app on their own shop (a normal, unprivileged action) and to be able to send HTTP requests to the app's public webhook endpoint with custom headers — no access to `api_secret_key`, tokens, or any credential is required. The `raw_body`+HMAC pair does not need to be forged, only replayed with a modified header, which requires no cryptographic secret.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable string used for HMAC verification, or otherwise cryptographically bind `shop` to the authenticated payload before it is trusted by handlers, e.g., by validating `request.shop` against the shop associated with the specific webhook subscription/session rather than trusting the raw header value.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` with the target app installed, and receives a genuine webhook: body `B`, header `X-Shopify-Hmac-SHA256: H` (valid for `B` under the shared `api_secret_key`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the request to the same endpoint with headers `X-Shopify-Hmac-SHA256: H`, `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, and the identical body `B`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully; `Utils::HmacValidator.validate` recomputes `HMAC(B, api_secret_key)` and it matches `H`, so validation passes.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed_body, ...))`, causing the app to process/act on data as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
