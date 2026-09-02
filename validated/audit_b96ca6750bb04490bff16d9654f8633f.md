Confirmed the finding with concrete evidence from `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`. The HMAC signature verified by `ShopifyAPI::Utils::HmacValidator.validate` only covers `@raw_body` (`to_signable_string` returns `@raw_body`, line 36-38 of `request.rb`), while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers (lines 15-33) and passed on trust to the app's handler as `WebhookMetadata` in `Registry.process` (`registry.rb` lines 188-199). The documentation explicitly tells app developers that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook" — i.e., it presents `shop` as verified/trusted, when it is not bound by the HMAC at all.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authenticated once `Utils::HmacValidator.validate(request)` succeeds, but that HMAC only signs the raw request body. The `shop-domain` header consumed as `request.shop` — and passed to every app's webhook handler as `WebhookMetadata#shop` — is never part of the signed payload, so it can be freely set by anyone who can reach the app's public webhook endpoint.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over that signable string and compares it with `secure_compare`: [2](#0-1) 
`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 
`Registry.process` only checks the body HMAC before forwarding `request.shop` (and the other unauthenticated header values) straight to the app's handler as trusted metadata: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that has installed the app (not per-tenant), a merchant who legitimately installed the app can trigger a real webhook for their own shop, capture the resulting `(raw_body, hmac)` pair, and then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a *different* victim shop's domain. The HMAC still validates because it never covered `shop` in the first place, so `Registry.process` accepts the forged attribution and calls the handler with `WebhookMetadata#shop` set to the victim shop.

### Impact Explanation
The library's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and describes `data.shop` as "The shop domain of the webhook," i.e. it is presented as a verified/trusted identity binding: [5](#0-4) 
Any host application that follows this documented contract and uses `data.shop` to select or scope per-tenant data (the standard pattern for multi-tenant Shopify apps) can be made to write, delete, or process data under a shop's identity that never sent the event, producing cross-tenant data corruption/access — this satisfies the "cross-tenant access" Critical bucket, since it breaks the equality `shop authenticated by HMAC == shop attributed to the event`.

### Likelihood Explanation
No credentials beyond the ability to install the app on any shop (or observe one delivered webhook) are required. This is an unprivileged-attacker path: the webhook HTTP endpoint is public by design, and constructing the forged request is trivial once a single valid `(body, hmac)` pair is obtained — the attacker never needs `api_secret_key` itself, only a legitimately delivered webhook.

### Recommendation
Include the shop domain (and other externally supplied metadata used for tenant routing, such as `topic`/`webhook_id`) in the HMAC-signed payload construction, or otherwise cryptographically bind them (e.g., look up the expected shop by an authenticated session/webhook subscription id rather than the raw header) before exposing them to the caller's webhook handler. At minimum, update the documentation to make explicit that `data.shop` is unauthenticated and must not be trusted for tenant-scoping decisions.

### Proof of Concept
1. App has `api_secret_key = S` and is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`.
2. A legitimate webhook for `shop-a` is delivered:
   - headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: HMAC(S, body)`
   - body: `{"id":1,...}`
3. Attacker (who controls `shop-a`, an unprivileged tenant of the app) intercepts/replays this exact `(body, hmac)` pair to the same webhook endpoint but swaps the header to `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(S, body)`, which is unchanged.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", topic: "orders/create", body: ...)`, as shown in `registry.rb` lines 198-199, causing the app to process `shop-a`'s order data under `shop-b`'s tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
