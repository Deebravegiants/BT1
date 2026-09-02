### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` only signs the raw JSON body when validating the webhook HMAC. The `shop-domain`, `topic`, `api-version`, and `webhook-id` values are read directly from unauthenticated HTTP headers and are never included in the signed bytes, yet `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` when dispatching to the merchant's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from request headers with no cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC over exactly `verifiable_query.to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` only asserts that this body HMAC is valid, then immediately builds `WebhookMetadata` using `request.shop` (an unauthenticated header) and hands it to the app's registered handler: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Here the equality does not hold — the HMAC only proves "this body was produced by Shopify for *some* shop that shares this app's secret," not "this body belongs to the shop named in the `shop-domain` header." Because Shopify signs `body` with the single app-wide `api_secret_key` (shared across all shops that install the app), any legitimate webhook payload/HMAC pair obtained from **the attacker's own shop** (a normal, low-privilege app install) remains a validly-signed pair for the app's secret. The attacker can then replay that exact body + HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (it never looked at the shop header), and `Registry.process` will pass `shop: <victim-domain>` to the handler, which the host application will treat as authoritative for routing/attributing the payload to the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged user who can install the app on their own store (or otherwise obtain one valid signed webhook body for their shop) can make the library report that data as belonging to an arbitrary victim shop domain, since the shop identifier is asserted rather than proven. Any host application that uses `WebhookMetadata#shop` (as returned by `Registry.process`) to select which merchant's record to update, without independently re-validating the shop against the signed payload, will attribute/act on the forged shop, which the gem's public contract advertises as reliable given `HmacValidator.validate` passed. This falls under cross-tenant access per the Critical impact bucket.

### Likelihood Explanation
No access token, `client_secret`, or privileged account is required — only the low-privilege action of installing/using the app on any shop (or otherwise capturing a single valid webhook body+HMAC pair) is needed to obtain a valid body/HMAC combination usable against every other tenant of the app, because the signing secret is shared across all shops using the same app credentials. The header (shop) can then be freely substituted.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise verify that the header-supplied shop is one the app has an active session/install for using a mechanism outside of the HMAC (e.g., cross-check against a stored list of installed shop domains) before dispatching to the handler. At minimum, `Registry.process` should not treat `request.shop` as trusted solely because the body HMAC validated.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`. Capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because computed over `B` with the app's shared `api_secret_key`), per `Request#to_signable_string`/`HmacValidator#compute_signature`. [1](#0-0) 
2. Replay the same body `B` and `hmac-sha256: H` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host application to act on/attribute the attacker's payload as belonging to the victim tenant. [6](#0-5)

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
