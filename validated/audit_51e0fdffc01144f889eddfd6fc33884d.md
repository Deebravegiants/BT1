### Title
Webhook `shop`, `topic`, `api-version`, and `webhook-id` fields are not covered by the HMAC signature, allowing shop-identity spoofing on replayed webhook deliveries - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the shop domain, topic, API version, and webhook id used to route and identify the webhook are taken from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Yet `shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates the request using only this HMAC-over-body check, then immediately trusts `request.topic`/`request.shop` to dispatch and construct the metadata handed to the app's handler: [3](#0-2) 

The equality the library implicitly claims to guarantee is:
`bytes verified by HMAC == identity (shop, topic) acted upon by the handler`

In reality the guarantee only covers the raw body bytes; the shop/topic headers are bytes that are parsed but never verified. Because HMAC-SHA256 over the body is independent of the header values, any request that reuses a previously-obtained valid `(raw_body, hmac)` pair will pass `Utils::HmacValidator.validate` regardless of what `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers are sent alongside it. [4](#0-3) 

An unprivileged internet user does not need the app's `client_secret` to obtain a valid `(raw_body, hmac)` pair — they only need to install the target app on their own (e.g. free development) store, which is the normal, unprivileged installation flow every public Shopify app supports. Shopify will deliver at least one legitimately signed webhook to the app's endpoint for that attacker-owned store. The attacker can then capture that exact `raw_body` + `X-Shopify-Hmac-Sha256` pair and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with an arbitrary victim shop's domain and a different registered topic. `Registry.process` will pass HMAC validation (body unchanged) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop and to whatever topic name is set in the (also-unverified) topic header. [5](#0-4) 

### Impact Explanation
Shopify webhook handlers built on top of this gem are documented to be looked up and acted on by shop domain (e.g. loading the stored offline session/access token for `data.shop`, or reacting to mandatory topics like `shop/redact`, `customers/data_request`, or `app/uninstalled` for that shop). Because this gem provides no verified binding between the signed bytes and the shop/topic identity it hands to the handler, an attacker who merely installs the app on their own store can forge deliveries that are misattributed to any other merchant's shop domain, causing the host application to execute privileged, shop-scoped business logic (data deletion/redaction flows, session/token revocation, order or inventory side effects, etc.) against a victim tenant using data the attacker fully controls. This is a cross-tenant identity-confusion vector rooted entirely in this gem's webhook verification code, not the host application's misuse of a documented API — the gem markets `Registry.process` as the mechanism that "will verify the request did indeed come from Shopify," per its own docs, while it only verifies the body bytes. [6](#0-5) 

### Likelihood Explanation
No credentials, secrets, or privileged access are required — an attacker simply needs to become a normal (free) merchant/installer of the target app, which any internet user can do for any public Shopify app, and capture one webhook delivery from their own shop. Replaying that captured body/HMAC pair with modified `shop`/`topic` headers is a trivial HTTP-level manipulation.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` (or at minimum `shop` and `topic`) in the HMAC-signed material used by `VerifiableQuery`/`HmacValidator`, or independently verify that the `X-Shopify-Shop-Domain` header corresponds to an actual known/authorized shop for the installed app (e.g., cross-check the shop against sessions the host app has stored) before constructing `WebhookMetadata` and invoking the handler. At minimum, document prominently that `request.shop`/`request.topic` are NOT covered by the HMAC and must not be trusted for authorization decisions without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (normal unprivileged install flow).
2. Shopify delivers a legitimate webhook to the app's endpoint, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: app/uninstalled
   X-Shopify-Hmac-Sha256: <valid-signature-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: {"id": 1}
   ```
3. Attacker captures the exact `Body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker replays the identical request but changes the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: app/uninstalled
   X-Shopify-Hmac-Sha256: <same-signature-as-captured>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 1}     <- unchanged, so HMAC still validates
   ```
5. `Utils::HmacValidator.validate(request)` succeeds because it only checks the (unchanged) body against the (unchanged) signature — see `lib/shopify_api/utils/hmac_validator.rb` lines 12-22 and `lib/shopify_api/webhooks/request.rb` lines 35-38.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) dispatches to the `app/uninstalled` handler with `shop: "victim-shop.myshopify.com"`, causing the host application to run its uninstall/cleanup logic for the victim shop even though the victim never uninstalled the app.

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
