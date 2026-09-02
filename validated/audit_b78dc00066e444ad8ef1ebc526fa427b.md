## Title
Webhook shop/topic identity spoofing – HMAC validates only the request body, not the `shop-domain`, `topic`, or `webhook-id` headers used for tenant routing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery#to_signable_string` by returning only the raw HTTP body [1](#0-0) , while the shop, topic and webhook-id used to route/authorize the payload are pulled straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` verifies only that the body's HMAC matches, then blindly trusts `request.shop`/`request.topic` to build the `WebhookMetadata` handed to the app's handler [3](#0-2) . This reproduces the report's bug class: a field ("shop" used as the effective tenant/session key) is acted upon but is not covered by the same authenticity check (HMAC) that is presented as proving the message came from that shop.

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(client_secret, verifiable_query.to_signable_string)` and time-safe-compares it to the `hmac` field [4](#0-3) . For webhook requests, `to_signable_string` is defined as `@raw_body` only [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors instead read directly from caller-supplied HTTP headers with no cryptographic binding to the signature [5](#0-4) .

`Registry.process` treats a passing HMAC check as proof of authenticity for the whole request, then uses the unauthenticated `request.shop` and `request.topic` to select the handler and construct the metadata object passed into app code [3](#0-2) . This is the same class of flaw as the reported issue: "field acted on but not covered by the [verification]" — here, the identity binding broken is:

`shop authenticated by HMAC` ≠ `shop used as the tenant key for routing/processing (request.shop)`

Because every shop that installs the app shares the same `client_secret` (there is one app-level secret, not a per-shop secret), any merchant who installs the app can obtain a legitimate `(raw_body, hmac)` pair for a webhook triggered by their own shop's events (e.g. `orders/create` with attacker-controlled order content). Since the headers are not part of the signed content, that attacker can replay the exact body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with a different, victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` then dispatches attacker-controlled body content tagged as belonging to the victim tenant.

### Impact Explanation
This crosses a tenant boundary: data nominally "signed" as coming from the app is actually attacker-chosen body content associated with an arbitrary victim shop. Depending on how the hosting app's webhook handler uses `WebhookMetadata#shop` (e.g., to look up which merchant's records to update, to trigger side effects scoped to that shop, or to key session/data stores), this enables cross-tenant data injection/spoofing without any credential belonging to the victim. This matches the Critical "cross-tenant access" impact category, since a request nominally authenticated for tenant A is processed as if it came from tenant B purely by an HTTP header substitution.

### Likelihood Explanation
Any user can become an "unprivileged internet user" from the app's perspective simply by installing the public app on their own store (a normal, permitted action) and triggering a real webhook event (e.g., creating an order) with content they control. They then replay the signed body with a forged `shop-domain` header to the app's public webhook URL. No access token, no `client_secret`, and no privileged account are required — only the ability to install the app and send an arbitrary HTTP POST.

### Recommendation
Bind the routing identity to the signature: derive the shop or reject the header if it disagrees with a shop identifier embedded in and covered by the signed payload, or maintain per-shop verification context so that a valid HMAC for shop A's raw body cannot be attributed to shop B. At minimum, cross-check `request.shop` against session/shop context established via other authenticated means (e.g., the shop tied to the offline access token used to originally register the webhook) before trusting it for routing, rather than trusting the raw header value once the (unrelated) body HMAC passes.

### Proof of Concept
1. Attacker installs the public Shopify app on `attacker-shop.myshopify.com` (unprivileged, self-service action).
2. Attacker triggers `orders/create` with attacker-controlled content; Shopify sends a webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`.
3. Attacker captures `(raw_body, hmac)` from this legitimate delivery.
4. Attacker POSTs the same `raw_body` and `hmac` to the app's public webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` in `lib/shopify_api/webhooks/registry.rb` line 190 passes because it only checks `raw_body` against the shared secret [6](#0-5) .
6. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's parsed order>, ...)` [7](#0-6) , causing the app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
