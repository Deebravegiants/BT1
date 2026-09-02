This confirms the vulnerability: the docs at `docs/usage/webhooks.md:125` explicitly claim `Registry.process` "will verify the request did indeed come from Shopify," and `data.shop` is documented as "The shop domain of the webhook" — the tenant identifier apps are expected to trust for routing/enqueueing per-shop work.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header to the app's handler as the trusted tenant identifier — without that header ever being covered by the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  This is the only input fed into `HmacValidator.validate`, which computes `HMAC(api_secret_key, signable_string)` and compares it to the `hmac` header: [2](#0-1)  Meanwhile `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read directly from unauthenticated HTTP headers: [3](#0-2) 

`Registry.process` validates only the HMAC, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3)  `WebhookMetadata.shop` is documented as "The shop domain of the webhook" that handlers use to route/attribute the event: [5](#0-4) 

The broken identity binding is:
`HMAC_valid(raw_body, api_secret_key) == true` **should imply** `shop header == shop that Shopify actually signed the payload for`

but in reality the equality only holds for the body bytes; the `shop-domain` header is never part of the signed material, so:
`HMAC_valid(raw_body) == true` ⇏ `request.shop == originating_shop`

Any actor who can obtain one valid `(raw_body, hmac)` pair for their own app installation — e.g., by installing the app on their own dev/test store and capturing a legitimate webhook Shopify sends them — can replay that exact body+HMAC pair while substituting an arbitrary `shop-domain` header (any victim's `*.myshopify.com` domain). `HmacValidator.validate` still passes because it only checks the body against the secret, and `Registry.process` forwards the attacker-chosen `shop` value to the handler as if it were verified. The `docs/usage/webhooks.md` explicitly promises that `Registry.process` "will verify the request did indeed come from Shopify," which is inaccurate for the shop identity — only body integrity/authenticity is verified. [6](#0-5) 

### Impact Explanation
Host applications are expected (and told by this gem's own docs) to key per-tenant business logic off `data.shop` (e.g., look up which merchant's record to update, which job queue/tenant context to enqueue into). Because `shop` is unauthenticated, an attacker with a valid HMAC secret only for their own shop can inject fabricated webhook events attributed to a different (victim) shop domain into the host app's processing pipeline — a cross-tenant data/identity confusion at the boundary this gem is responsible for authenticating. This satisfies the "cross-tenant access" criterion for a Critical-class impact, since the entire purpose of `Registry.process`/`HmacValidator` is to establish a trustworthy shop identity for the webhook payload, and it fails to bind the shop header to the signature.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any Shopify store the attacker controls (trivial for any public/development app), (2) capturing one legitimately signed webhook body+HMAC pair from that installation, and (3) replaying it to the app's public webhook endpoint with a modified `shopify-shop-domain`/`x-shopify-shop-domain` header pointing at a victim shop. No access token, `api_secret_key`, or privileged credentials are needed — this is fully reachable by an unprivileged internet user who can register any Shopify store.

### Recommendation
Bind the shop (and ideally topic/webhook-id) to the authenticated material: either include the `shop-domain` header in the signable string used for HMAC computation, or require callers of `Registry.process` to independently verify `request.shop` against an already-authenticated session/shop record before trusting it, and document clearly that `HmacValidator` only authenticates body bytes, not headers.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker-shop.myshopify.com`; trigger any subscribed webhook topic so Shopify sends a legitimately signed webhook to the app's endpoint.
2. Capture the raw request: body `B` and header `x-shopify-hmac-sha256: H` (valid for `HMAC(api_secret_key, B)`).
3. Replay a POST to the same webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` passes (body/HMAC match), `Registry.process` calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, even though Shopify never sent this payload for `victim-shop`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
