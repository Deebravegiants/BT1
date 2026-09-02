## Analysis Result

### Title
Webhook `topic` and `shop` are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `topic` and `shop` values used to route and label the webhook, however, are read directly from HTTP headers that are never included in the signed material. This breaks the intended identity binding `HMAC-verified sender == claimed shop/topic`, allowing an attacker who possesses any one valid `(body, hmac)` pair to replay it with a forged `shop-domain`/`topic` header pair.

### Finding Description
`Registry.process` performs exactly one check before dispatching to the app's handler: [1](#0-0) 

`Utils::HmacValidator.validate(request)` calls `request.to_signable_string`, which is defined to be only the raw body: [2](#0-1) 

But `topic` and `shop` — the values that determine which handler runs and which tenant the payload is attributed to — are pulled straight from HTTP headers with **no cryptographic binding to the HMAC**: [3](#0-2) 

`HmacValidator.validate` itself only ever operates on `verifiable_query.to_signable_string` and `verifiable_query.hmac`: [4](#0-3) 

So the equality the gem *should* enforce is:
`HMAC-authenticated body == (topic, shop) attributed to that body`

What is actually enforced is only:
`HMAC(secret, raw_body) == received_signature`

`topic` and `shop-domain` sit outside that boundary entirely. Any attacker who can obtain one legitimately-signed `(raw_body, hmac)` pair — trivial to do, since anyone can install a Shopify app on a store they control and simply capture a webhook Shopify sends to that app's public callback endpoint — can replay that exact body/HMAC pair directly to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (a different, victim tenant) and/or `X-Shopify-Topic` header (a different handler than the one the payload was actually meant for).

`Registry.process` then hands this forged identity straight to the app's business logic: [5](#0-4) 

The handler receives `WebhookMetadata` claiming the data came from `shop: request.shop` even though the HMAC never certified that shop value.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler cannot distinguish a genuinely-authorized-for-that-shop webhook from an attacker-forged one, because the `shop` and `topic` fields are unauthenticated. An attacker (a normal, unprivileged merchant who installed the app on their own store) can:
- Attribute their own webhook payload to a victim shop (`shop-domain` forgery), causing the host app to process/store data under the wrong tenant.
- Redirect a legitimately-signed body to an unrelated handler by forging `topic` (e.g. routing an ordinary payload into a `customers/redact` or `shop/redact` handler), potentially triggering destructive/mandatory-compliance logic against a shop the attacker doesn't own.

This matches the Critical "cross-tenant access" impact category, since it lets one tenant's authenticated payload be attributed to and processed against another tenant's identity, without needing the app's `client_secret`, an access token, or any other privileged credential.

### Likelihood Explanation
Likelihood is high for any app exposing a webhook endpoint using this gem's `Webhooks::Registry`/`Webhooks::Request` as documented: the webhook endpoint is a public HTTP endpoint by design (Shopify calls it over the internet), and nothing in this gem restricts the caller to Shopify's IP ranges or otherwise authenticates the request beyond the body HMAC. Obtaining a valid `(body, hmac)` pair requires only installing the app on an attacker-owned/controlled store — a normal, unprivileged action — and capturing one delivered webhook.

### Recommendation
Include `topic` and `shop-domain` (and ideally `webhook-id`/`api-version`) in the signed/verified material, or otherwise cryptographically bind them to the body before trusting them for routing/attribution — e.g. verify the HMAC over a canonicalized string that incorporates these header values, or require the host application to independently cross-check `shop` against a known/expected value (e.g. the session tied to the endpoint) before dispatching to a handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers to receive a webhook (any topic).
2. Shopify sends a webhook to the app's public callback URL; attacker captures the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid because `H = HMAC(api_secret_key, B)`).
3. Attacker sends their own POST request directly to the same public webhook endpoint with:
   - Body: `B` (unchanged, so the HMAC still validates)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Topic: customers/data_request` (or any topic of attacker's choosing, if the app has a matching handler)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`.
5. The app handler is invoked with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the app to act on `B`'s content as if it were an authentic webhook from `victim-shop.myshopify.com`.

### Citations

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
