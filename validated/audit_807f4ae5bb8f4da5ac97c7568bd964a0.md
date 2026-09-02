### Title
Webhook shop-domain / topic / webhook_id headers are trusted but not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers. Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any request whose body byte-for-byte matches a previously-observed legitimate webhook produces the same valid HMAC regardless of which shop's `x-shopify-shop-domain` header is attached. This breaks the intended binding `hmac(body) == hmac_for(shop, body)` down to `hmac(body) == hmac(body)`, letting an attacker replay a legitimate webhook payload with a forged `shop-domain` header pointing at a victim tenant.

### Finding Description
`Registry.process` performs exactly one check before invoking the topic handler: [1](#0-0) 

The HMAC validation call goes to `Utils::HmacValidator.validate`, which computes the signature only from `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns solely the raw body — none of the identifying headers are part of the signed material: [3](#0-2) 

Yet `shop`, `topic`, and `webhook_id` — all parsed straight from attacker-controlled HTTP headers with no cryptographic binding — are exactly the fields the handler uses to decide which tenant's data/session the payload belongs to: [4](#0-3) [5](#0-4) 

Because the HMAC secret is the app's single `client_secret` (`Context.api_secret_key`), not a per-shop key, the signature is identical for identical bodies regardless of originating shop. An attacker who can obtain one validly-signed webhook body (e.g., by installing the app on their own low-value/trial shop, or intercepting/observing a webhook they legitimately receive) can retransmit that same body to the app's webhook endpoint with the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header changed to a victim shop domain, and the HMAC check passes unchanged, because those header bytes were never part of what was verified.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem authenticates "this body came from Shopify" but the host application (following the gem's documented `Registry.process` contract) is led to believe "this body came from shop X" using the unauthenticated header. Any host app that uses `WebhookMetadata#shop` to route webhook side effects (updating order/inventory/customer records, revoking access, decrementing balances, etc. for the named shop) can be made to apply an attacker-replayed payload to an arbitrary victim shop's data, i.e., cross-tenant access/data corruption caused entirely by trusting a field the gem itself validates incorrectly (a spec/body signature that omits the tenant-identifying header).

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own webhook body of a type they control the shape of (many webhook bodies for common events like `app/uninstalled`, `shop/update`, or custom app-metafield webhooks can be triggered by the attacker's own shop actions), and (2) sending a forged HTTP request to the app's public webhook endpoint with a substituted `shop-domain` header — no access token, no `client_secret`, and no privileged account is needed. This is reachable by any unprivileged internet user who can install the app on a shop they control and can reach the app's public webhook callback URL.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`/`api_version`) values in the signed material verified for webhooks, or otherwise cryptographically bind them to the body before the handler trusts them — e.g., verify the HMAC over `shop-domain + raw_body` (matching what Shopify would need to sign) rather than raw body alone, or, at minimum, have host applications compare the header's `shop` against the shop already known/expected for the reached endpoint. Since this requires a change to what the shared secret protects, the recommended immediate mitigation is to document that `request.shop` must be corroborated against an independent trusted source (e.g., a fixed webhook path per shop, or a shop known via active session) before being used to route side effects, and consider extending `to_signable_string` for webhook requests if Shopify's real signing scheme permits it.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives (or triggers) a legitimate webhook with body B and valid
# HMAC H = HMAC_SHA256(client_secret, B). Because H depends only on B and
# the *shared* client_secret (identical for every shop of this app),
# the attacker can replay it as:

headers = {
  "x-shopify-topic"       => "orders/create",     # unchanged, still valid for H
  "x-shopify-hmac-sha256" => H,                    # captured, still valid for B
  "x-shopify-shop-domain" => "victim.myshopify.com", # forged - unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (only B and H are checked)
# => handler.handle receives WebhookMetadata(shop: "victim.myshopify.com", ...)
# => host app applies attacker-controlled payload B to victim's tenant data
``` [6](#0-5)

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
