### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly and unauthenticated from HTTP headers. `Registry.process` validates only the body's HMAC and then dispatches the handler using these unauthenticated header values as the trusted tenant identity, breaking the equality: *bytes verified by HMAC (raw body) ≠ bytes the identity decision is based on (shop-domain header)*.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` performs exactly one check — `Utils::HmacValidator.validate(request)` over the body — and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` recomputes the HMAC over the same signable string and does a constant-time comparison, but again only over body bytes: [4](#0-3) 

Because none of `shop-domain`, `topic`, or `webhook-id` are part of the signed material, any party who has previously observed one legitimately-signed webhook delivery (raw body + `X-Shopify-Hmac-Sha256`) — for example the operator of any shop that has installed the app and can view webhooks delivered to their own endpoint — can replay that exact body/HMAC pair to the same webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header to name a different, victim shop. `Registry.process` will still report `Utils::HmacValidator.validate(request)` as `true` because the body bytes and secret are unchanged, and the handler will then execute business logic attributing the event to the attacker-chosen victim shop.

### Impact Explanation
This breaks the identity binding *shop the HMAC actually authenticates == shop the application acts on behalf of*, enabling cross-tenant confusion: a handler that looks up sessions/data keyed by `WebhookMetadata#shop` and trusts it because the request "passed HMAC validation" can be made to process attacker-supplied body content as if it originated from an arbitrary other merchant's shop. This is a **Critical – cross-tenant access** class issue per the stated impact bands, since it lets an unprivileged app-installer forge cross-tenant events without any credential beyond having observed one prior legitimate delivery to their own store.

### Likelihood Explanation
Likelihood is realistic: any merchant who installs the app receives real webhooks with valid HMACs for their own shop domain and can trivially capture raw body + `X-Shopify-Hmac-Sha256` from their own endpoint logs, then replay it with modified `shop-domain`/`topic`/`webhook-id` headers to the shared webhook endpoint. No access to `api_secret_key`, access tokens, or other shops' credentials is required — only observation of one's own legitimately-delivered webhook.

### Recommendation
Bind the tenant/topic identity into the signed material or otherwise reject unverifiable header trust: e.g., include `shop`, `topic`, and `webhook_id` in the signable string (mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for OAuth params), or require the consuming application to independently verify `shop` against a known/registered shop before dispatching, and add replay protection (e.g., enforce/validate `webhook_id` uniqueness) so a captured body+HMAC pair cannot be re-delivered under a different identity.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery at their controlled endpoint: raw body `B` with header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `client_secret`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the identical `B`/`H` pair to the app's public webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and, if desired, `X-Shopify-Topic`/`X-Shopify-Webhook-Id` to a topic/id of their choosing).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` (`request.rb#to_signable_string`) — this still matches `H`, so validation succeeds.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled `victim.myshopify.com` value and invokes the registered handler, which processes body `B` as if it were an authentic event from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
