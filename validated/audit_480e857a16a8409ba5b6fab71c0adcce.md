### Title
Webhook `shop-domain` Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an incoming webhook using an HMAC computed only over the raw request body, but the `shop` (merchant) identity attached to the webhook is read from an unauthenticated HTTP header that is never included in the signed payload. This breaks the identity binding `shop_authenticated == shop_attributed_to_data`, allowing an attacker to inject an arbitrary shop domain into a signature-valid webhook.

### Finding Description
The HMAC that Shopify (or any holder of the same `client_secret`) computes for a webhook only signs the raw JSON body: [1](#0-0) 

The `shop` value used downstream, however, is pulled directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is completely outside the signed content: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop` to build the metadata handed to the app's handler, without ever binding it to the signature: [3](#0-2) 

`HmacValidator.validate` confirms this: it calls `verifiable_query.to_signable_string`, which for `Request` is just `@raw_body`, and never touches headers such as `shop`: [4](#0-3) [1](#0-0) 

Because the app's `client_secret` (`Context.api_secret_key`) is the *same* secret used to sign webhooks for every shop that has installed the app, any unprivileged merchant who installs the app on their own store can capture a genuinely-signed webhook body (or any body they can get validly HMAC'd for a topic they control) and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. The signature still validates (it only covers the body), but `WebhookMetadata.shop` — which the host application uses to determine which tenant's session/data to update — now falsely claims to be the victim shop.

### Impact Explanation
This crosses a tenant boundary: the gem hands the host application webhook data falsely attributed to a shop the attacker does not control, using a validly-signed (from the gem's perspective) request. Any application logic keyed on `WebhookMetadata#shop` (e.g., updating shop-scoped records, triggering shop-specific side effects, or acting as if a specific merchant's data changed) can be manipulated by an unprivileged attacker who is simply a legitimate installer of the app on their own store. This matches the Critical "cross-tenant access" impact category, since data/actions can be incorrectly bound to another merchant's tenant.

### Likelihood Explanation
Any developer/merchant who installs the app (an unprivileged, standard flow) obtains the ability to trigger genuinely-signed webhook deliveries for their own shop (e.g., by performing actions that fire webhooks). They can intercept/replay that HTTP request to the app's public webhook endpoint while altering only the `shop-domain` header — no access to `client_secret`, tokens, or the victim's environment is required. The vulnerability is fully within the gem's `Request`/`Registry`/`HmacValidator` code path and does not depend on the host app deviating from documented usage.

### Recommendation
Extend `to_signable_string` (or a dedicated verification step in `HmacValidator`/`Registry.process`) to bind the `shop-domain` header into the signed material, or otherwise cross-check the header-derived shop against an independently authenticated value (e.g., verify it matches the shop associated with a previously established, authenticated session) before constructing `WebhookMetadata`. At minimum, document/enforce that `shop` must not be trusted for tenant-scoping decisions unless it is itself covered by the HMAC.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimately triggered webhook, e.g. body `{"id":123}` with header `x-shopify-hmac-sha256: <valid HMAC of body using app's client_secret>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body/HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC only over `@raw_body` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the app's handler executes shop-scoped logic against the victim shop's tenant, despite the request never having been produced by or for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
