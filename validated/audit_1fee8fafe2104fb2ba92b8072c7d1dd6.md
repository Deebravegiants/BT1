This confirms the vulnerability. The docs explicitly state that `Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), and apps are expected to trust `data.shop` as the tenant identity binding (docs/usage/webhooks.md:14, 25-26) — but the `shop` field is never covered by the HMAC signature.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are excluded from HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only this body-derived HMAC and then dispatches `request.shop` straight into `WebhookMetadata` for the handler to consume as the tenant identity [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop header value == shop that the HMAC-validated body was actually generated for`. In this gem that equality is never enforced — the HMAC is computed with `Digest.hexencode(...)` over `@raw_body` only [1](#0-0) , and `shop` is pulled from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cross-check against the body or any registered shop list [4](#0-3) .

`HmacValidator.validate` only ever compares `verifiable_query.hmac` against a signature computed from `verifiable_query.to_signable_string`, i.e. the body [5](#0-4) . Crucially, `api_secret_key` is the app's single client secret, shared across every shop that has installed the (public) app — it is not shop-specific. This means a webhook `(body, hmac)` pair that validates correctly for one shop's webhook delivery will validate identically for the same body regardless of which shop-domain header accompanies it, because the header is outside the signed data.

An unprivileged attacker who has installed the target app on their own store (a normal, legitimate installation path for any public Shopify app) legitimately receives real webhook deliveries with a valid `(raw_body, hmac)` pair addressed to their own shop. They can then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., the victim's shop). `Utils::HmacValidator.validate` still succeeds because the HMAC only covers `raw_body` [6](#0-5) , and `Registry.process` forwards the forged `shop` value straight to the handler as authoritative tenant identity [7](#0-6) .

This is structurally the same bug class as the reported Bribe.sol issue: a value that participates in a security-relevant accounting/identity decision (`totalVoting` there, `shop` here) is mutated/read outside the path that is cryptographically committed to (the `deposit`/`withdraw` checkpoint there, the HMAC-signed body here), breaking the implicit invariant the rest of the system relies on.

### Impact Explanation
The gem's own documentation instructs consuming applications to trust `data.shop` from `WebhookMetadata` as the shop identity for the webhook (see `docs/usage/webhooks.md` lines 10-26), and states that `Registry.process` "will verify the request did indeed come from Shopify" (line 125) — implying the whole payload, including shop, is authenticated. Any host application following this documented contract (e.g., looking up the merchant record by `data.shop`, then applying `data.body` to it) can be made to apply attacker-controlled webhook bodies to a victim shop's record, or misattribute events cross-tenant, purely by header manipulation with no possession of the victim's session, access token, or `client_secret`. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Any internet user can achieve this: install the public app once on a shop they control (or use a free development store), capture one legitimate webhook `(body, hmac)` pair sent to their own endpoint, then POST it to the app's webhook route with a spoofed `shop-domain` header. No secrets, tokens, or elevated access are required — only the documented, unprivileged `ShopifyAPI::Webhooks::Registry.process` entry point is used exactly as intended.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the verified signature domain, or at minimum require host applications to cross-validate `request.shop` against a list of shops known to have valid, registered sessions/installations before trusting it — and make this an enforced check inside `Registry.process` rather than leaving it to be independently discovered by every integrator. Concretely, `Registry.process` could require the caller to supply/verify the expected shop (e.g., resolved from an existing session store) before invoking the handler, rather than blindly trusting the unauthenticated header value.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store; register a webhook (e.g. `orders/create`) pointing at the app's public webhook endpoint.
2. Trigger the webhook naturally (e.g., create an order) and capture the raw POST: headers (`x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`) and `raw_body: B`.
3. Replay to the same endpoint with `x-shopify-shop-domain` changed to `victim-shop.myshopify.com`, keeping `raw_body: B` and `x-shopify-hmac-sha256: H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate` succeeds because it only hashes `B` [1](#0-0) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` [8](#0-7) , causing the host application to process attacker-controlled data under the victim shop's identity.

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
