### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying the HMAC over the raw body, but the `shop` value that the gem hands to the app's handler is read from an unauthenticated HTTP header that is never included in the signed bytes. This breaks the intended binding "HMAC-verified bytes == the shop this webhook is attributed to."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — recomputes the HMAC over `to_signable_string` (the raw body only) and compares it to the `hmac` header: [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `request.shop` (the unauthenticated header value) is forwarded verbatim into `WebhookMetadata`, which the app's handler is documented to trust as "The shop domain of the webhook": [5](#0-4) [6](#0-5) 

The identity equality the gem is supposed to enforce is:
`HMAC-verified(raw_body, client_secret) == the tenant (shop) the app attributes this event to`

In reality the gem only proves `HMAC-verified(raw_body, client_secret)` and separately trusts `header["shop-domain"]` with no cryptographic link between the two. Because `client_secret` is the same for every shop that installs a given app (it is a property of the app, not of the shop), any merchant who installs the app on their own store can obtain genuine `(raw_body, valid_hmac)` pairs from Shopify's real webhook deliveries to their store. That attacker can then replay the exact same body/HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and the handler receives `data.shop == "victim-shop.myshopify.com"` with attacker-controlled `data.body`, i.e. a forged, gem-authenticated event that appears to originate from another tenant.

### Impact Explanation
This directly enables cross-tenant confusion inside any host application that relies on the gem's documented `WebhookMetadata#shop` value to select which tenant's data to update from a "verified" webhook (e.g. dispatching `orders/create`, `app/uninstalled`, `shop/redact`, etc. against the wrong shop record). Since the gem itself asserts the request "did indeed come from Shopify" (per its own docs) once `HmacValidator.validate` passes, and the shop attribution is folded into that same trusted result object, this qualifies as a cross-tenant identity-binding break reachable by an unprivileged attacker who only needs to be a legitimate installer of the target app on their own store — no access token, API secret, or privileged account is required.

### Likelihood Explanation
Likelihood is moderate: the attacker must (a) install the same app on a shop they control (a normal, unprivileged action for any public app) and (b) be able to replay an HTTP POST with a chosen `shop-domain` header to the app's public webhook callback URL, which is by design internet-reachable and unauthenticated aside from the HMAC. Both actions require no elevated privileges and no possession of the app's `client_secret`.

### Recommendation
Bind the shop identity into the authenticated material before trusting it, e.g. by including the `shop-domain` (and/or `webhook-id`/`topic`) header value in the bytes covered by `to_signable_string`, or by cross-checking the header-derived shop against an independently verified source (such as the shop associated with the specific `webhook_id` returned from a server-side lookup) before constructing `WebhookMetadata`. At minimum, the documentation should explicitly warn that `data.shop` is not covered by the HMAC and must not be used as a sole tenant-selection key.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com`; Shopify delivers a legitimate webhook (e.g. `orders/create`) to the app's callback with headers `shopify-hmac-sha256: <validHMAC>`, `shopify-shop-domain: attacker.myshopify.com`, and body `B`.
2. Attacker captures `(B, validHMAC)` — both are unauthenticated over the wire (or simply reusable, since neither leaks the secret nor is bound to shop).
3. Attacker sends `POST /callback/orders/create` directly to the app with the same body `B`, same `shopify-hmac-sha256: validHMAC`, but header `shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds: [3](#0-2) 
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...)`, and the host app processes attacker-controlled data as if it were a verified event from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
