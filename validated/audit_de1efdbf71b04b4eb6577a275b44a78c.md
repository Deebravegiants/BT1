### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Utils::HmacValidator` authenticates a webhook exclusively by validating the HMAC over `Webhooks::Request#to_signable_string`, which returns only the raw HTTP body. The `shop` and `topic` values that `ShopifyAPI::Webhooks::Registry.process` treats as the authenticated identity of the event are read straight from unauthenticated HTTP headers and are never included in the signed content. Because this gem's app-level `api_secret_key` is shared across every shop that installs the app, any attacker who can obtain one genuinely-signed `(body, hmac)` pair (trivially available to them by installing the app on their own store and generating an event) can replay that pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `topic`) header for a victim shop, and the signature check still passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Webhooks::Request#shop` and `#topic` are parsed directly from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes/verifies the HMAC solely over `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof of authenticity for the *entire request*, then forwards the unauthenticated `request.shop` and `request.topic` to the app's handler as the trusted identity of the event: [4](#0-3) 

The equality this breaks: `hmac` should authenticate `(shop, topic, body)` as a bound tuple, but it only authenticates `body`. Since `api_secret_key` is one shared value for the whole app (not per-shop), any tenant of the app can generate a validly-signed body for *any* topic they can trigger in their own store, then relabel it as coming from a different shop by editing the `x-shopify-shop-domain` header — an unprivileged action requiring no possession of the app's `client_secret`/`api_secret_key` and no privileged account on the victim shop.

### Impact Explanation
This crosses a tenant boundary: it lets one merchant (an unprivileged, low-cost attacker who has installed the app on any store, including a free/dev store) forge webhook events attributed to a store they do not control. Depending on the app's webhook handlers, this can be used to inject spoofed `orders/create`, `app/uninstalled`, `customers/data_request`, `shop/redact`, or other topic-specific events for a victim shop, potentially triggering unauthorized state changes, notifications, GDPR-style data actions, or business logic keyed on the (falsely attributed) shop identity. This is a cross-tenant access issue.

### Likelihood Explanation
High. All ingredients are attacker-obtainable with no elevated privileges: (1) install/use the target app on a store the attacker controls to legitimately receive a Shopify-signed webhook for a topic of interest, capturing the raw body + `x-shopify-hmac-sha256` value; (2) POST that exact body/HMAC pair to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to the victim's domain. No secret material, TLS interception, or social engineering is needed — only network access to the app's public webhook URL.

### Recommendation
Bind `shop` (and ideally `topic`) into the value that is HMAC-verified, e.g. verify a canonical string composed of `shop|topic|raw_body` (or require and independently validate the shop against session/install records before trusting `request.shop`), rather than trusting the `x-shopify-shop-domain`/`x-shopify-topic` headers as authenticated solely because the body's HMAC passed.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and performs an action that triggers a webhook the app subscribes to (e.g., `orders/create`), capturing the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (H = HMAC-SHA256(app.api_secret_key, B), which is valid since `api_secret_key` is shared across all shops for this app).
2. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256: H`, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only, and it matches `H`, so validation succeeds.
4. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though the event body actually originated from `attacker-shop.myshopify.com`, and the app's own logic processes it as a legitimate event for the victim shop.

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
