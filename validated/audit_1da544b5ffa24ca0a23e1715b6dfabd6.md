### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then blindly trusts the `shop-domain` header (and `topic`/`webhook_id`) to build the `WebhookMetadata` passed to the app's handler. The HMAC never covers these headers, so any attacker who can produce one validly-signed body/HMAC pair can freely rewrite the `shop-domain` header to any other tenant's domain, and the library will hand that attacker-controlled `shop` value to the app as if it were authenticated.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature against `verifiable_query.to_signable_string`. For webhook requests, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, the `shop` accessor used by the handler dispatch comes from an HTTP header that is never mixed into the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC and then forwards `request.shop` (from the unauthenticated header) straight into `WebhookMetadata`, which is delivered to the app's handler as the tenant identity for the event: [3](#0-2) 

The documentation explicitly tells integrators that `process` "will verify the request did indeed come from Shopify," implying full authentication of the payload including its tenant attribution: [4](#0-3) 

This breaks the identity binding: `hmac_valid(raw_body) == true` is treated as equivalent to `shop_header == authenticated_shop`, but the two are independent — the HMAC secret (`api_secret_key`) is the same for every shop that installed a given app, so any actor who has captured one legitimately-signed webhook body (e.g., from their own installed test shop) can replay it with a forged `x-shopify-shop-domain` header pointing at a different merchant. `Registry.process` will still accept it, since only `@raw_body` is checked.

### Impact Explanation
This allows cross-tenant confusion: an attacker-controlled `shop` value reaches the app's webhook handler with the same trust level as a value that came directly from Shopify, letting an attacker attribute a validly-signed payload to any arbitrary shop domain of their choosing. Any app that keys per-tenant logic (looking up sessions/access tokens, applying data updates, billing, deprovisioning, etc.) off `WebhookMetadata#shop` without an independent check is exposed to cross-tenant data corruption or actions being taken against the wrong merchant, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one validly HMAC-signed webhook body — trivially available to any developer who installs the target app on their own store and captures the resulting webhook call (the signing secret is shared across all shops using the app, not shop-specific). No access token, `api_secret_key`, or privileged access is required beyond that.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the material verified against the HMAC, or otherwise cryptographically bind them to the signed body before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. At minimum, the gem should not offer `shop`, `topic`, and `webhook_id` as verified/trusted fields once HMAC validation succeeds, and documentation should make clear that only the raw body is authenticated, not the headers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker replays the exact same body `B` and signature `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, and the app performs the webhook's associated action against `victim.myshopify.com`'s data/session, even though Shopify never sent this event for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
